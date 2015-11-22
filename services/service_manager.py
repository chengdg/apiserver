# -*- coding: utf-8 -*-

from db.account.models import User, UserProfile
from wapi.member.models import WebAppUser, Member
from wapi.member.models import SocialAccount

EVENT2SERVICE = {}

def register(event):
	def register_wrapper(func):
		EVENT2SERVICE[event] = func
		#for k,v in EVENT2SERVICE.items():
		#	print("{} => {}".format(k, v))
		return func
	return register_wrapper
	

class FakeRequest(object):
	def __init__(self, full_path='unknown'):
		self.full_path = full_path

	def get_full_path(self):
		return self.full_path



def create_request(args):
	request = FakeRequest(args.get('full_path','unknown'))
	request.GET = args['GET']
	request.COOKIES = args['COOKIES']
	request.method = args['method']
	request.POST = args['POST']
	request.META = dict()

	data = args['data']
	app_id = data['app_id']
	user_id = data['user_id']
	webppuser_id = data['webppuser_id']
	user_profile_id = data['user_profile_id']
	social_account_id = data['social_account_id']
	member_id = data['member_id']
	request.app = None
	request.user = User.get(id=user_id) if user_id != -1 else None
	request.social_account = SocialAccount.get(id=social_account_id) if social_account_id != -1 else None
	request.member = Member.get(id=member_id) if member_id != -1 else None
	request.user_profile = UserProfile.get(id=user_profile_id) if user_profile_id != -1 else None
	request.webapp_user = WebAppUser.get(id=webppuser_id) if webppuser_id != -1 else None
	request.visit_data = args['visit_data']
	if request.user_profile:
		request.webapp_owner_id = request.user_profile.user_id
	else:
		request.webapp_owner_id = -1

	# if request.user:
	# 	request.user.is_from_mobile_phone = data['is_user_from_mobile_phone']
	# 	request.user.is_from_weixin = data['is_user_from_weixin']
	return request


def call_service(event, args):
	print("deprecated!")
	EVENT2SERVICE[event](create_request(args), args)

