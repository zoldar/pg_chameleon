import rollbar
import yaml
import os, os.path
import sys
import logging
from logging.handlers  import TimedRotatingFileHandler
from distutils.sysconfig import get_python_lib
from shutil import copy

class rollbar_notifier(object):
	"""
		This class is used to send messages to rollbar whether the key and environment variables are set
	"""
	def __init__(self, rollbar_key, rollbar_env, rollbar_level, logger):
		"""
			Class constructor.
		"""
		self.levels = {
				"critical": 1, 
				"error": 2, 
				"warning": 3, 
				"info": 5
			}
		self.rollbar_level = self.levels[rollbar_level]
		self.logger = logger
		self.notifier = rollbar
		if rollbar_key !='' and rollbar_env != '':
			self.notifier.init(rollbar_key, rollbar_env)  
		else:
			self.notifier = None
		
		
	def send_message(self, message, level):
		"""
			The method sends a message to rollbar. If it fails it just logs an error 
			without causing the process to crash.
		"""
		if self.notifier:
			exc_info = sys.exc_info()
			try:
				notification_level = self.levels[level]
				if notification_level <= self.rollbar_level:
					try:
						self.notifier.report_message(message, level)
						if exc_info[0]:
							self.notifier.report_exc_info(exc_info)
					except:
						self.logger.error("Could not send the message to rollbar.")
			except:
				self.logger.error("Wrong rollbar level specified.")

class config_lib(object):
	def __init__(self, config):
		self.config_name = config
		python_lib=get_python_lib()
		cham_dir = "%s/.pg_chameleon" % os.path.expanduser('~')	
		self.local_conf = "%s/configuration/" % cham_dir 
		self.global_file = '%s/global-config.yml' % self.local_conf
		
		self.configuration_files = {}
		global_config = []
		config_example = []
		
		config_example.append('%s/pg_chameleon/configuration/config-example.yml' % python_lib)
		config_example.append('%s/config-example.yml' % self.local_conf)
		
		global_config.append('%s/pg_chameleon/configuration/global-config.yml' % python_lib)
		global_config.append('%s/global-config.yml' % self.local_conf)
		
		self.configuration_files["config_example"] = config_example
		self.configuration_files["global_config"] = global_config
		
		local_logs = "%s/logs/" % cham_dir 
		local_pid = "%s/pid/" % cham_dir 
		
		self.conf_dirs=[
			cham_dir, 
			self.local_conf, 
			local_logs, 
			local_pid, 
			
		]
		try:
			self.__load_globals()
			self.load_config()
		except FileNotFoundError:
			pass
			
	
	def __load_globals(self):
		"""
			The method loads the global variables set in the global-config.yml.
			This ensures the fundamental values are correctly set whether the configuration file is present or not.
		"""
		config_file = open(self.global_file, 'r')
		self.global_config = yaml.load(config_file.read())
		config_file.close()
		self.config=dict(self.global_config.items())
		
	def init_configuration(self):
		""" 
			The method loops the list self.conf_dirs creating them only if they are missing.
			
			The method checks the freshness of the config-example.yaml and connection-example.yml 
			copies the new version from the python library determined in the class constructor with get_python_lib().
			
			If the configuration file is missing the method copies the file with a different message.
		
		"""

		for confdir in self.conf_dirs:
			if not os.path.isdir(confdir):
				print (self.INFO_CREATE_DIR .format(directory=confdir))
				os.mkdir(confdir)
		
		for conf in self.configuration_files:
			source = self.configuration_files[conf][0]
			destination = self.configuration_files[conf][1]
			if os.path.isfile(destination):
				if os.path.getctime(source)>os.path.getctime(destination):
					print (self.INFO_UPDATE_CONF_FILE.format(file=destination))
					copy(source, destination)
			else:
				print (self.INFO_COPY_CONF_FILE.format(file=destination))
				copy(source, destination)
	
		
	def load_config(self):
		""" 
			The method loads the configuration from the file specified in the args.config parameter.
		"""
		
		self.config_file = '%s/%s.yml'%(self.local_conf, self.config_name)
		
		if not os.path.isfile(self.config_file):
			print("**FATAL - configuration file missing. Please ensure the file %s is present." % (self.config_file))
			sys.exit()
		
		config_file = open(self.config_file, 'r')
		config = yaml.load(config_file.read())
		config_file.close()
		self.config = dict(self.global_config, **config)
		

class logger_lib(object):
	def __init_logger(self, logger_name):
		"""
		The method initialise a new logger object using the configuration parameters.
		The formatter is different if the debug option is enabler or not.
		The method returns a new logger object and sets the logger's file descriptor in the class variable 
		logger_fds, used when the process is demonised.
		
		:param logger_name: the name of the logger used to build the file name and get the correct logger
		:return: list with logger and file descriptor
		:rtype: list

		"""
		log_dir = self.config["log_dir"] 
		log_level = self.config["log_level"] 
		log_dest = self.config["log_dest"] 
		log_days_keep = self.config["log_days_keep"] 
		config_name = self.args.config
		source_name = self.args.source
		debug_mode = self.args.debug
		if source_name == '*':
			log_name = "%s_general" % (config_name)
		elif  logger_name == "global":
			log_name = "%s_%s" % (config_name, source_name)
		else:
			log_name = "%s_%s_%s" % (config_name, source_name, logger_name)
		
		log_file = os.path.expanduser('%s/%s.log' % (log_dir,log_name))
		logger = logging.getLogger(logger_name)
		logger.setLevel(logging.DEBUG)
		logger.propagate = False
		if debug_mode:
			str_format = "%(asctime)s %(processName)s %(levelname)s %(filename)s (%(lineno)s): %(message)s"
		else:
			str_format = "%(asctime)s %(processName)s %(levelname)s: %(message)s"
		formatter = logging.Formatter(str_format, "%Y-%m-%d %H:%M:%S")
		
		if log_dest=='stdout' or debug_mode:
			fh=logging.StreamHandler(sys.stdout)
			
		elif log_dest=='file':
			fh = TimedRotatingFileHandler(log_file, when="d",interval=1,backupCount=log_days_keep)
		
		if log_level=='debug' or debug_mode:
			fh.setLevel(logging.DEBUG)
		elif log_level=='info':
			fh.setLevel(logging.INFO)
			
		fh.setFormatter(formatter)
		logger.addHandler(fh)
		logger_fds = fh.stream.fileno()
		return [logger, logger_fds]
