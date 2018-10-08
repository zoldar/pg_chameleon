import gettext
from distutils.sysconfig import get_python_lib
python_lib=get_python_lib()


class msg_translate(object):
	def __init__(self, locale):
		"""
		Class constructor
		"""
		locale_dir = '%s/pg_chameleon/locale' % (python_lib, )
		trn = gettext.translation('log_msg', localedir=locale_dir, languages=[locale])
		#trn.install()
		_ = trn.gettext
		# replica.py messages
		self.WARN_UPGRADE_MODE =  _("WARNING, entering upgrade mode. Disabling the catalogue version's check. Expected version {expected}, installed version {installed}")
		self.WARN_CATALOGUE_MISMATCH = _("WARNING, catalogue mismatch. Expected version {expected}, installed version {installed}")
		self.FATAL_CATALOGUE_MISMATCH = _("FATAL, replica catalogue version mismatch. Expected {expected}, got {installed}")
		self.FATAL_SOURCE_NOT_REGISTERED = _("FATAL, the source {source} is not registered. Please add the source with the command add_source --source {source}")
		self.INFO_STOP_REPLICA = _("Caught stop replica signal terminating daemons and ending the replica process")
		self.INFO_CREATE_DIR = _("creating directory {directory}")
		self.INFO_UPDATE_CONF_FILE =  _("updating {file}")
		self.INFO_COPY_CONF_FILE =  _("copying {file}")
		self.FATAL_MISSING_CONF_FILE =  _("FATAL, configuration file missing. Please ensure the file {file} is present.")
		self.INFO_CREATE_REPLICA_SCHEMA = _("Trying to create replica schema")
		self.INFO_DROP_REPLICA_SCHEMA = _("Dropping the replica schema")
		self.FATAL_MISSING_SOURCE = _("FATAL, no source name specified. You must specify a source name with the argument --source")
		self.INFO_ADD_NEW_SOURCE = _("Trying to add a new source")
		self.INFO_DROP_SOURCE_CONFIRM = _("Dropping the source {source} will remove drop any replica reference.\n Are you sure? YES/No\n")
		self.INFO_DROP_SOURCE = _("Trying to remove the source")
		self.WARN_UPPERCASE_CONFIRM =  _("Please type YES all uppercase to confirm")
	
		# mysql_lib.py
		self.INFO_INIT_SOURCE = _("starting init replica for source {source}")
