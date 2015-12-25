#coding: utf8
"""
资源抽取器
"""
from business import model as business_model 

class ResourceExtractor(business_model.Model):
	"""
	资源抽取器base class
	"""
	__slots__ = (
	)

	def __init__(self, webapp_owner, webapp_user):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user
