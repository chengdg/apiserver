#coding: utf8
"""
积分资源抽取器
"""

from business import model as business_model 
from business.mall.resource.resource_extractor import ResourceExtractor

class IntegralResourceExtractor(ResourceExtractor):
	"""
	积分资源抽取器
	"""

	__slots__ = (
		)

	def __init__(self, webapp_owner, webapp_user):
		ResourceExtractor.__init__(self, webapp_owner, webapp_user)

	def __allocate_integral_sale(self, webapp_owner, order, purchase_info):
		"""
		申请积分应用活动

		@note 感觉这段代码是检查积分是否可用。(by Victor)

		@see 从`order_integral_resource_allocator.py`移植过来

		@retval is_success: 如果成功，返回True；否则，返回False
		@retval reason: 如果成功，返回None；否则，返回失败原因
		"""
		count_per_yuan = webapp_owner.integral_strategy_settings.integral_each_yuan

		group2integralinfo =  purchase_info.group2integralinfo
		uid2group = dict((group.uid, group) for group in order.product_groups)
		for group_uid, integral_info in group2integralinfo.items():
			promotion_product_group = uid2group[group_uid]

			if not promotion_product_group.active_integral_sale_rule:
				#当purchase_info提交的信息中存在group的积分信息
				#但是该group当前没有了active_integral_sale_rule
				#意味着商品的积分应用已经过期
				reason = {
					'type': 'integral:integral_sale:expired',
					'msg': u'积分折扣已经过期',
					'short_msg': u'已经过期'
				}
				self.__supply_product_info_into_fail_reason(promotion_product_group.products[0], reason)
				return False, reason


			use_integral = int(integral_info['integral'])
			integral_money = round(float(integral_info['money']), 2)
			
			# 校验前台输入：积分金额不能大于使用上限、积分值不能小于积分金额对应积分值
			# 根据用户会员与否返回对应的商品价格
			product_price = sum([product.price * product.purchase_count for product in promotion_product_group.products])
			integral_sale_rule = promotion_product_group.active_integral_sale_rule
			max_integral_price = round(product_price * integral_sale_rule['discount'] / 100, 2)
			if max_integral_price < (integral_money - 0.01) \
				or (integral_money * count_per_yuan) > (use_integral + 1):
				reason = {
					'type': 'integral:integral_sale:exceed_max_integral_limit',
					'msg': u'使用积分不能大于促销限额',
					'short_msg': u'使用积分不能大于促销限额'
				}
				self.__supply_product_info_into_fail_reason(promotion_product_group.products[0], reason)
				return False, reason

		return True, None

	def extract(self, order, purchase_info):
		"""
		根据purchase_info抽取积分的资源

		@see order_integral_resource_allocator.py
		@return order和Resource对象
		"""
		resources = []

		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		#count_per_yuan = webapp_owner.integral_strategy_settings.integral_each_yuan
		total_integral = 0
		#integral_money = 0
		if purchase_info.order_integral_info:
			#使用积分抵扣
			#is_success, reason = self.__allocate_order_integral_setting(webapp_owner, order, purchase_info)
			#if not is_success:
			#	return False, reason, None

			total_integral = purchase_info.order_integral_info['integral']
			resource = IntegralResource.get({
					'webapp_owner': webapp_owner,
					'webapp_user': webapp_user,
					'type': self.resource_type,
				})
			# 表示待使用的积分
			resource.integral = total_integral

			# 相当于emit一个resource
			resources.append(resource)

		elif purchase_info.group2integralinfo:
			#使用积分应用
			is_success, reason = self.__allocate_integral_sale(webapp_owner, order, purchase_info)
			if not is_success:
				return False, reason, None

			for group_uid, integral_info in purchase_info.group2integralinfo.items():
				total_integral += int(integral_info['integral'])

			resource = IntegralResource.get({
					'webapp_owner': webapp_owner,
					'webapp_user': webapp_user,
					'type': self.resource_type,
				})
			# 表示待使用的积分
			resource.integral = total_integral
			# 相当于emit一个resource
			resources.append(resource)

		#integral_resource_allocator = IntegralResourceAllocator(webapp_owner, webapp_user)
		#is_success, reason, resource = integral_resource_allocator.allocate_resource(total_integral)
		return order, resources

	@property
	def resource_type(self):
		return business_model.RESOURCE_TYPE_INTEGRAL
