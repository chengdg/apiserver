# -*- coding: utf-8 -*-
from business import model as business_model
from db.mall import promotion_models
from business.resource.coupon_resource import CouponResource


class CouponResourceAllocator(business_model.Service):
	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

	def allocate_resource(self, coupon):
		"""
		申请优惠券资源
		"""
		member_id = self.context['webapp_user'].member.id

		coupon_resource = CouponResource.get({
			'type': self.resource_type,
		})

		coupon_resource.coupon = coupon
		coupon_resource.money = coupon.money

		coupon_resource.raw_status = coupon.status
		coupon_resource.raw_member_id = coupon.member_id

		promotion_models.Coupon.update(status=promotion_models.COUPON_STATUS_USED).where(
			promotion_models.Coupon.id == coupon.id).execute()

		if not coupon.member_id:
			promotion_models.CouponRule.update(remained_count=promotion_models.CouponRule.remained_count - 1).dj_where(id=coupon.coupon_rule.id).execute()

		promotion_models.CouponRule.update(use_count=promotion_models.CouponRule.use_count + 1).dj_where(id=coupon.coupon_rule.id).execute()

		# 更新红包优惠券分析数据 by Eugene
		red_envelope2member = promotion_models.RedEnvelopeParticipences.select().dj_where(coupon_id=coupon.id).first()
		if red_envelope2member:
			if red_envelope2member.introduced_by != 0:
				promotion_models.RedEnvelopeParticipences.update(
					introduce_used_number=promotion_models.RedEnvelopeParticipences.introduce_used_number + 1).dj_where(
					red_envelope_rule_id=red_envelope2member.red_envelope_rule_id,
					red_envelope_relation_id=red_envelope2member.red_envelope_relation_id,
					member_id=red_envelope2member.introduced_by).execute()
			self.red_envelope2member = red_envelope2member
		return True, '', coupon_resource

	@staticmethod
	def release(resource):
		"""
		释放优惠券资源
		"""
		if resource.coupon:
			promotion_models.Coupon.update(status=resource.raw_status,
			                               member_id=resource.raw_member_id).where(
				promotion_models.Coupon.id == resource.coupon.id).execute()
			if not resource.raw_member_id:
				promotion_models.CouponRule.update(remained_count=promotion_models.CouponRule.remained_count + 1).dj_where(id=resource.coupon.coupon_rule.id).execute()

			promotion_models.CouponRule.update(use_count=promotion_models.CouponRule.use_count - 1).dj_where(id=resource.coupon.coupon_rule.id).execute()

			red_envelope2member = resource.red_envelope2member
			if red_envelope2member and red_envelope2member.introduced_by != 0:
				promotion_models.RedEnvelopeParticipences.update(
						introduce_used_number=promotion_models.RedEnvelopeParticipences.introduce_used_number - 1).dj_where(
						red_envelope_rule_id=red_envelope2member.red_envelope_rule_id,
						red_envelope_relation_id=red_envelope2member.red_envelope_relation_id,
						member_id=red_envelope2member.introduced_by).execute()

	@property
	def resource_type(self):
		return business_model.RESOURCE_TYPE_COUPON
