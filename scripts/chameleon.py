#!/usr/bin/env python
from pkg_resources import get_distribution
__version__ = get_distribution('pg_chameleon')
import argparse
from pg_chameleon.replica import replica_engine
from pg_chameleon.msg.log_msg import chameleon_translate
trn = chameleon_translate()
commands = [
	'show_config',
	'show_sources',
	'show_status', 
	'create_replica_schema',
	'drop_replica_schema',
	'upgrade_replica_schema',
	'add_source',
	'drop_source',
	'init_replica',
	'enable_replica',
	'update_schema_mappings',
	'refresh_schema',
	'sync_tables',
	'start_replica', 
	'stop_replica', 
	'detach_replica', 
	'init_configuration', 
	'update_configuration', 
	'show_errors', 
	'run_maintenance', 
	'stop_all_replicas'
	]

command_help = ','.join(commands)

schema_help = """Specifies the schema within a source. If omitted all schemas for the given source are affected by the command. Requires the argument --source to be specified"""
source_help = """Specifies the source within a configuration. If omitted all sources are affected by the command."""
tables_help = """Specifies the tables within a source . If omitted all tables are affected by the command."""
logid_help = """Specifies the log id entry for displaying the error details"""
debug_help = """Forces the debug mode with logging on stdout and log level debug."""
version_help = """Displays pg_chameleon's installed  version."""
rollbar_help = """Overrides the level for messages to be sent to rolllbar. One of: "critical", "error", "warning", "info". The Default is "info" """
full_help = """When specified with run_maintenance the switch performs a vacuum full instead of a normal vacuum. """


parser = argparse.ArgumentParser(description=trn.PARSE_DESC,  add_help=True)
parser.add_argument('command', type=str, help=command_help)
parser.add_argument('--config', type=str,  default='default',  required=False, help=trn.CONFIG_HELP)
parser.add_argument('--schema', type=str,  default='*',  required=False, help=trn.SCHEMA_HELP)
parser.add_argument('--source', type=str,  default='*',  required=False, help=trn.SOURCE_HELP)
parser.add_argument('--tables', type=str,  default='*',  required=False, help=trn.TABLES_HELP)
parser.add_argument('--logid', type=str,  default='*',  required=False, help=trn.LOGID_HELP)
parser.add_argument('--debug', default=False, required=False, help=trn.DEBUG_HELP, action='store_true')
parser.add_argument('--version', action='version', help=trn.VERSION_HELP,version='{version}'.format(version=__version__))
parser.add_argument('--rollbar-level', type=str, default="info", required=False, help=trn.ROLLBAR_HELP)
parser.add_argument('--full', default=False, required=False, help=trn.FULL_HELP, action='store_true')
args = parser.parse_args()


replica = replica_engine(args)
if args.debug:
	getattr(replica, args.command)()
else:
	try:
		getattr(replica, args.command)()
	except AttributeError:
		print("ERROR - Invalid command" )
		print(command_help)
