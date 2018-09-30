import gettext
class msg_translate(object):
	def __init__(self, locale="en_GB"):
		"""
		Class constructor
		"""
		self.init_translate(locale)
		
	def init_translate(self, locale):
		trn = gettext.translation('log_msg', localedir='locale', languages=[locale])
		trn.install()
			
		self.INIT_START_SOURCE = _("starting init replica for source %s")
