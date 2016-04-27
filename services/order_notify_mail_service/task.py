# -*- coding: utf-8 -*-

import db.account.models as accout_models
from db.mall import models as mall_models
from db.mall import promotion_models
from eaglet.core.service.celery import task

import settings
from core.exceptionutil import unicode_full_stack
from core.sendmail import sendmail
from eaglet.core import watchdog
from features.util.bdd_util import set_bdd_mock


@task(bind=True)
def notify_order_mail(self, user_id, member_id, status, oid, order_id, buyed_time, order_status, total_price, bill, coupon, coupon_money, integral, buyer_name, buyer_address, buyer_tel, remark, postage='0', express_company_name=None, express_number=None):
		"""
		发送邮件，通知订单消息

		@todo 用模板改造沟通邮件内容的代码
		"""
		if coupon:
			coupon = str(promotion_models.Coupon.get(id=int(coupon)).coupon_id) + u',￥' + str(coupon_money)
		else:
			coupon = ''

		order_has_products = mall_models.OrderHasProduct.select().dj_where(order=oid)
		buy_count = ''
		product_name = ''
		product_pic_list = []
		for order_has_product in order_has_products:
			buy_count = buy_count+str(order_has_product.number)+','
			product_name = product_name+order_has_product.product.name+','
			product_pic_list.append(order_has_product.product.thumbnails_url)
		buy_count = buy_count[:-1]
		product_name = product_name[:-1]


		order_notify = accout_models.UserOrderNotifySettings.select().dj_where(user_id=user_id, status=status, is_active=True).first()
		if order_notify and str(member_id) not in order_notify.black_member_ids.split('|') and order_notify.emails != '':
			# TODO: 可以用模板改造这段代码
			content_list = []
			content_described = u'微商城-%s-订单' % order_status
			if order_id:
				if product_name:
					content_list.append(u'商品名称：%s' % product_name)
				if product_pic_list:
					pic_address = ''
					for pic in product_pic_list:
						if pic.find('http') < 0:
							pic = "http://%s%s" % (settings.WEAPP_DOMAIN, pic)
						pic_address = pic_address+"<img src='%s' width='170px' height='200px'></img>" % (pic)
					if pic_address != '':
						content_list.append(pic_address)
				content_list.append(u'订单号：%s' % order_id)
				if buyed_time:
					content_list.append(u'下单时间：%s' % buyed_time)
				if order_status:
					content_list.append(u'订单状态：<font color="red">%s</font>' % order_status)
				if express_company_name:
					content_list.append(u'<font color="red">物流公司：%s</font>' % express_company_name)
				if express_number:
					content_list.append(u'<font color="red">物流单号：%s</font>' % express_number)
				if buy_count:
					content_list.append(u'订购数量：%s' % buy_count)
				if total_price:
					content_list.append(u'支付金额：%s' % total_price)
				if integral:
					content_list.append(u'使用积分：%s' % integral)
				if coupon:
					content_list.append(u'优惠券：%s' % coupon)
				if bill:
					content_list.append(u'发票：%s' % bill)
				if postage:
					content_list.append(u'邮费：%s' % postage)
				if buyer_name:
					content_list.append(u'收货人：%s' % buyer_name)
				if buyer_tel:
					content_list.append(u'收货人电话：%s' % buyer_tel)
				if buyer_address:
					content_list.append(u'收货人地址：%s' % buyer_address)
				if remark:
					content_list.append(u'顾客留言：%s' % remark)

				# if member_id:
				# 	try:
				# 		member = Member.objects.get(id=member_id)
				# 		content_list.append(u'会员昵称：%s' % member.username_for_html)
				# 	except:
				# 		pass

			content = u'<br> '.join(content_list)
			if settings.IS_UNDER_BDD:
				mock = dict()
				mock_content = {
					'buyer_name':buyer_name,
					'buy_count': buy_count,
					'buyer_address': buyer_address,
					'buyer_tel': buyer_tel,
					'order_status': order_status,
					'product_name': product_name,
					'total_price': total_price,
					'integral': integral,
					'coupon': coupon
				}
				mock['mails'] = order_notify.emails
				mock['content'] = mock_content
				set_bdd_mock('notify_mail', mock)
				return
			__send_email(user_id, order_notify.emails, content_described, content)

def __send_email(user_id, emails, content_described, content):
	try:
		for email in emails.split('|'):
			if email.find('@') > -1:
				sendmail(email, content_described, content)
	except:
		notify_message = u"发送邮件失败user_id（{}）, cause:\n{}".format(user_id,unicode_full_stack())
		watchdog.warning(notify_message)
