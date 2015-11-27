#coding: utf8
import os,sys
#import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'polaris.settings')

from wapi.mall.models import *
from db.account.models import User # 对应 django.auth.models.User

def dump(categories):
	print("============================")
	for category in categories:
		print("id:{}, user:{}, name:{}, pic_url:{}, created_at:{}".format(category.id, category.owner.username, category.name.encode('utf8'), category.pic_url.encode('utf8'), category.created_at.strftime('%Y-%m-%d %H:%M')))


if __name__ == "__main__":
	user = User.select().where(User.username == 'jobs')

	user = User.get(User.id == 1)
	print("user: {}".format(user))

	# 创建记录
	category = ProductCategory.create(owner=user, name="分类XX", pic_url="http://someplace/", product_count=0)
	category2 = ProductCategory(owner=user, name="分类ZZ", pic_url='')
	category2.save()

	#c = ProductCategory.get(ProductCategory.id == 1)
	#print("category: {}".format(c))

	# 查询
	categories = ProductCategory.select()
	dump(categories)

	categories = ProductCategory.select().where(ProductCategory.name  == "分类XX")
	dump(categories)

	categories = ProductCategory.filter(name="分类ZZ")
	dump(categories)

	product = Product.get(id=10)
	print(product)

