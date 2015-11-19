# -*- coding: utf-8 -*-

__author__ = 'bert'

WEIXIN_API_PROTOCAL = 'https'
WEIXIN_API_DOMAIN = 'api.weixin.qq.com'


API_GET= 'get'
API_POST= 'post'

API_CLASSES = {
	'get_user_info': 'core.wxapi.api_get_user_info.WeixinUserApi',
	'create_qrcode_ticket': 'core.wxapi.api_create_qrcode_ticket.WeixinCreateQrcodeTicketApi',
	'get_qrcode': 'core.wxapi.api_get_qrcode.WexinGetQrcodeApi',
	'create_customerized_menu': 'core.wxapi.api_customerized_menu.WeixinCreateCustomerizedMenuApi',
	'delete_customerized_menu': 'core.wxapi.api_customerized_menu.WeixinDeleteCustomerizedMenuApi',
	'get_customerized_menu': 'core.wxapi.api_customerized_menu.WeixinGetCustomerizedMenuApi',
	'get_groups': 'core.wxapi.api_get_groups.WeixinGroupsApi',
	'send_custom_msg': 'core.wxapi.api_send_custom_msg.WeixinSendCustomMsgApi',
	'get_member_group_id': 'core.wxapi.api_get_member_groupid.WeixinGetMemberGroupIdApi',
	'upload_media_image': 'core.wxapi.api_upload_media.WeixinUploadMediaImageApi',
	'upload_content_media_image': 'core.wxapi.api_upload_media.WeixinUploadContentMediaImageApi',
	'upload_media_voice': 'core.wxapi.api_upload_media.WeixinUploadMediaVoiceApi',
	'upload_media_news': 'core.wxapi.api_upload_news.WeixinUploadNewsApi',
	'send_mass_message': 'core.wxapi.api_send_mass_message.WeixinMassSendApi',
	'create_deliverynotify': 'core.wxapi.api_pay_delivernotify.WeixinPayDeliverNotifyApi',
	'send_template_message': 'core.wxapi.api_send_template_message.WeixinTemplateMessageSendApi',
	'delete_mass_message': 'core.wxapi.api_delete_mass_message.WeixinDeleteMassMessageApi',
	'get_component_token': 'core.wxapi.api_component_token.WeixinComponentToken',
	'api_create_preauthcode': 'core.wxapi.api_create_preauthcode.WeixinCreatePreauthcode',
	'api_query_auth': 'core.wxapi.api_query_auth.WeixinQueryAuth',
	'api_authorizer_token': 'core.wxapi.api_authorizer_token.WeixinGetAuthorizerToken',
	'api_get_authorizer_info': 'core.wxapi.api_get_authorizer_info.WeixinGetAuthorizerInfo',
	'api_shakearound_device_aopplyid':'core.wxapi.api_shakearound_device_applyid.WeixinShakeAroundDeviceApplyid',
	'api_get_user_summary':'core.wxapi.api_get_user_analysis.WeixinGetUserSummaryApi',
	'api_get_user_cumulate':'core.wxapi.api_get_user_analysis.WeixinGetUserCumulateApi',
	}