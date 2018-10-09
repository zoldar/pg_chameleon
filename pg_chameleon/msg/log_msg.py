import gettext
from distutils.sysconfig import get_python_lib
from pg_chameleon.lib.global_lib import config_lib
python_lib=get_python_lib()


class chameleon_translate(object):
	def __init__(self):
		"""
		Class constructor
		"""
		cnf=config_lib()
		try:
			locale = cnf.config["locale"]
		except AttributeError:
			locale = "en_GB"
		locale_dir = '%s/pg_chameleon/locale' % (python_lib, )
		trn = gettext.translation('log_msg', localedir=locale_dir, languages=[locale])
		#trn.install()
		_ = trn.gettext
		self.PARSE_DESC = _("""Command line for pg_chameleon""")
		self.CONFIG_HELP = _("""Specifies the configuration to use without the suffix yml. If  the parameter is omitted then ~/.pg_chameleon/configuration/default.yml is used.""")
		self.SCHEMA_HELP = _("""Specifies the schema within a source. If omitted all schemas for the given source are affected by the command. Requires the argument --source to be specified.""")
		self.SOURCE_HELP = _("""Specifies the source within a configuration. If omitted all sources are affected by the command.""")
		self.TABLES_HELP = _("""Specifies the tables within a source . If omitted all tables are affected by the command.""")
		self.LOGID_HELP = _("""Specifies the log id entry for displaying the error details""")
		self.DEBUG_HELP = _("""Forces the debug mode with logging on stdout and log level debug""")
		self.VERSION_HELP = _("""Displays pg_chameleon's installed  version""")
		self.ROLLBAR_HELP = _("""Overrides the level for messages to be sent to rolllbar. One of: "critical", "error", "warning", "info". The Default is "info".""")
		self.FULL_HELP = _("""When specified with run_maintenance the switch performs a vacuum full instead of a normal vacuum""")

		
class msg_translate(object):
	def __init__(self):
		"""
		Class constructor
		"""
		cnf=config_lib()
		try:
			locale = cnf.config["locale"]
		except AttributeError:
			locale = "en_GB"
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
