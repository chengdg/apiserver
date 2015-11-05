from wapi.mall.models import Product
p = Product.select().where(id=9)
print p
print p.get().name