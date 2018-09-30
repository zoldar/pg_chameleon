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
		print(locale_dir)
		trn = gettext.translation('log_msg', localedir=locale_dir, languages=[locale])
		trn.install()
			
		self.INIT_START_SOURCE = _("starting init replica for source %s")
