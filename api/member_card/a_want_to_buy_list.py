# -*- coding: utf-8 -*-
"""
会员卡-我想买列表
"""
from eaglet.core import api_resource
from eaglet.core import watchdog
from eaglet.core import paginator
from eaglet.decorator import param_required

from business.member_card.want_to_buy import WantToBuy
from business.account.ad_clicked import AdClicked
from business.member_card.member_card import MemberCard

MY_WANT_TO_BUY_PAGE_PARAM = 1  #我发表的
MY_SUPPORT_PAGE_PARAM = 2  #我支持的
DEFAULT_COUNT_PER_PAGE = 10
WANT_TO_BUY_PAGE_TYPE = 2
class AWantToBuyList(api_resource.ApiResource):
	"""
	会员卡-我想买列表
	"""
	app = 'member_card'
	resource = 'want_to_buy_list'

	@param_required(['cur_page'])
	def get(args):
		"""
		@param page 可选参数，1 我发表的，2 我支持的，不带此参数则显示全部数据
		@return want_to_buy_list
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		is_binded = webapp_user.is_binded
		member_id = webapp_user.member.id

		if not is_binded:  #如果没绑定手机则直接返回
			return {'is_binded': False}

		member_card = MemberCard.from_member_id({
			"member_id": member_id
		})
		is_vip = True if member_card else False
		if not is_vip:  #如果不是会员则直接返回
			return {
				'is_binded': is_binded,
				'is_vip': is_vip
			}

		#是否点击过广告蒙版
		ad_clicked = AdClicked.from_member_id({
				"member_id": member_id,
				"type": WANT_TO_BUY_PAGE_TYPE
			})

		is_ad_clicked = True if ad_clicked else False

		page = int(args.get('page', '0'))
		items = []
		if page == MY_WANT_TO_BUY_PAGE_PARAM:
			items = WantToBuy.get_my_list({
				'webapp_owner': webapp_owner,
				'member_id': member_id
			})
		elif page == MY_SUPPORT_PAGE_PARAM:
			items = WantToBuy.get_my_support_list({
				'webapp_owner': webapp_owner,
				'member_id': member_id
			})
		else:
			items = WantToBuy.get_all_list({
				'webapp_owner': webapp_owner
			})

		#分页
		count_per_page = int(args.get('count_per_page', DEFAULT_COUNT_PER_PAGE))
		cur_page = int(args['cur_page'])
		pageinfo, items = paginator.paginate(items, cur_page, count_per_page)

		_items = []
		for item in items:
			_item = item.to_dict()
			_item['is_can_support'] = False  #是否显示“支持一下”按钮
			if is_binded and is_vip and not item.has_supported(member_id) and item.member_id != member_id:
				_item['is_can_support'] = True

			_item['is_show_view_progress'] = False  #是否显示“查看采购进度”按钮
			if is_binded and is_vip and item.is_success:
				_item['is_show_view_progress'] = True

			_items.append(_item)

		return {
			'is_binded': True,
			'is_vip': is_vip,
			'is_ad_clicked': is_ad_clicked,
			'items': _items,
			'page_info': pageinfo.to_dict()
		}
