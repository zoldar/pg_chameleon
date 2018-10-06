import rollbar
import yaml
import os, os.path
import sys
from distutils.sysconfig import get_python_lib
import logging
from logging.handlers  import TimedRotatingFileHandler

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
	def __init__(self):
		python_lib=get_python_lib()
		cham_dir = "%s/.pg_chameleon" % os.path.expanduser('~')	
		local_conf = "%s/configuration/" % cham_dir 
		self.global_conf_example = '%s/pg_chameleon/configuration/config-example.yml' % python_lib
		self.local_conf_example = '%s/config-example.yml' % local_conf
		local_logs = "%s/logs/" % cham_dir 
		local_pid = "%s/pid/" % cham_dir 
		
		self.conf_dirs=[
			cham_dir, 
			local_conf, 
			local_logs, 
			local_pid, 
			
		]
		self.load_config()
	def load_config(self):
		""" 
			The method loads the configuration from the file specified in the args.config parameter.
		"""
		local_confdir = "%s/.pg_chameleon/configuration/" % os.path.expanduser('~')	
		self.config_file = '%s/%s.yml'%(local_confdir, self.args.config)
		
		if not os.path.isfile(self.config_file):
			print("**FATAL - configuration file missing. Please ensure the file %s is present." % (self.config_file))
			sys.exit()
		
		config_file = open(self.config_file, 'r')
		self.config = yaml.load(config_file.read())
		config_file.close()
		

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
