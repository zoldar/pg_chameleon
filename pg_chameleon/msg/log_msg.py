import gettext
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.sysconfig import get_python_lib
python_lib=get_python_lib()

class msg_translate(object):
	def __init__(self, locale="en_GB"):
		"""
		Class constructor
		"""
		self.init_translate(locale)
		
	def init_translate(self, locale):
		locale_dir = '%s/pg_chameleon/locale' % (python_lib, )
		trn = gettext.translation('log_msg', localedir=locale_dir, languages=[locale])
		trn.install()
		
		# global_lib.py
		self.WARN_UPGRADE_MODE =  _("WARNING, entering upgrade mode. Disabling the catalogue version's check. Expected version %s, installed version %s")
		self.WARN_CATALOGUE_MISMATCH = _("WARNING, catalogue mismatch. Expected version %s, installed version %s")
		self.FATAL_CATALOGUE_MISMATCH = _("FATAL, replica catalogue version mismatch. Expected %s, got %s")
		self.FATAL_SOURCE_NOT_REGISTERED = _("FATAL, the source %s is not registered. Please add the source with the command add_source")
		
		# mysql_lib.py
		self.INIT_START_SOURCE = _("starting init replica for source %s")
