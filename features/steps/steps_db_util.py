# -*- coding: utf-8 -*-

from db.mall.models import (
    PostageConfig, ProductModelProperty, ProductModelPropertyValue,
    OrderHasProduct, Order, Product, PAYTYPE2NAME, ORDER_TYPE2TEXT,
    STATUS2TEXT, ORDER_SOURCE_WEISHOP, ProductModel,
     PRODUCT_MODEL_PROPERTY_TYPE_IMAGE, PayInterface, Province, City, District
)

from features.util import bdd_util
from db.member.models import WebAppUser
from db.mall.promotion_models import Coupon


def get_product_model_keys(product_model_name):
    """使用规格名获取获取规格key
    @param product_model_name 规格名使用逗号分隔，类似于：男,M,红色
    @return 规格key，类似于12:58_13:62_14:59
    """
    if product_model_name and product_model_name != 'standard':
        values = ProductModelPropertyValue.objects.filter(name__in=product_model_name.split(','))
        values = ['%s:%s' % (value.property_id, value.id) for value in values]
        return '_'.join(values)
    return 'standard'

def get_postage_config(owner_id, name):
    return PostageConfig.objects.get(name=name, owner_id=owner_id)


def get_product_model_property(webapp_owner_id):
    name2id = {}
    id2name = {}
    property_ids = [
        property.id for property in ProductModelProperty.select().dj_where(
                                        owner_id=webapp_owner_id,
                                        is_deleted=False)
    ]
    property_values = ProductModelPropertyValue.select().dj_where(
        property_id__in=property_ids,
        is_deleted=False
    )
    for property_value in property_values:
        name = property_value.name
        id = '%d:%d' % (property_value.property_id, property_value.id)
        # TODO to fix bug. jz
        name2id[name] = id
        id2name[id] = name

    return name2id, id2name


def get_custom_model_id_from_name(webapp_owner_id, model_name):
    #获取所有product model property value
    name2id, _ = get_product_model_property(webapp_owner_id)

    model_property_value_names = model_name.split(' ')
    value_ids = [name2id[model_property_value_name] for model_property_value_name in model_property_value_names]
    value_ids = '_'.join(value_ids)
    return value_ids


def get_custom_model_id_from_user_code(webapp_owner_id, user_code):
    """
    不赞成使用
    """
    return ProductModel.objects.get(owner_id=webapp_owner_id, user_code=user_code)


def get_custom_model_name_from_id(webapp_owner_id, model_id):
    #获取所有product model property value
    _, id2name = get_product_model_property(webapp_owner_id)
    names = []
    for model_property_value_id in model_id.split('_'):
        names.append(id2name[model_property_value_id])
    return ' '.join(names)


def get_product_response_from_web_page(context, product_name):
    existed_product = Product.objects.get(
        owner_id=context.webapp_owner_id,
        name=product_name)
    response = context.client.get('/mall2/product/?id=%d' % existed_product.id)

    return response


#########################################
# order相关
#########################################


def get_order_by_order_id(order_id):
    try:
        return Order.objects.get(order_id=order_id)
    except:
        return None

def get_coupon_by_id(id):
    try:
        return Coupon.objects.get(id=id)
    except:
        return None

def get_product_by_prouduct_id(owner_id,name):
    try:
        return Product.objects.get(owner_id=owner_id,name=name)
    except:
        return None

def get_order_has_products(context):
    order = Order.objects.get(order_id=context.pay_order_id)
    order_has_products = None
    if hasattr(context.response, 'order_has_products'):
        order_has_products = context.response.context['order_has_products']
    else:
        order_has_products = OrderHasProduct.objects.filter(order=order)
    return order, order_has_products


def get_latest_order():
    try:
        return Order.objects.filter(origin_order_id__lte=0).order_by('-id')[0]
    except:
        return None

#########################


# def get_order_has_delivery_times_by_order_id(order_id):
#     try:
#         return OrderHasDeliveryTime.objects.filter(order_id=order_id)
#     except:
#         return None

def set_order_dict(order, profile):
    """
    order -> {
        'status':
        'logistics':
        'type':
        'methods_of_payment':
        'member':
        'order_no':
        'number':
        'integral':
        'ship_name':
        'ship_tel':
        'order_time':
        'products':

    }
    """
    status = _get_status_by_name(order.get('status'))
    express_value = express_util.get_value_by_name(order.get('logistics'))
    type = _get_type_by_name(order.get('type'))
    pay_interface_type = _get_paytype_by_name(order.get('methods_of_payment'))
    webapp_user_id = 1
    if order.get('member'):
        webapp_user_name = order.get('member')
        member = bdd_util.get_member_for(webapp_user_name, profile.webapp_id)
        try:
            webapp_user_id = WebAppUser.objects.get(member_id=member.id).id
        except:
            pass
    area = get_area_ids(order.get('ship_area', None))
    order_model = OrderFactory(
        order_id=order.get('order_no'),
        express_company_name=express_value,
        express_number=order.get('number', ''),
        status=status,
        webapp_id=profile.webapp_id,
        type=type,
        pay_interface_type=pay_interface_type,
        integral=order.get('integral', 0),
        webapp_user_id=webapp_user_id,
        ship_name=order.get('ship_name', u'收货人'),
        ship_tel=order.get('ship_tel', u'1333333333'),
        webapp_source_id=profile.webapp_id,
        ship_address=order.get('ship_address', ''),
        area=area
    )
    order_model.product_price = 0
    if order.get('order_time'):
        order_model.created_at = order.get('order_time')
        order_model.save()

    if order.get('sources') == u"商城":
        order_model.order_source = ORDER_SOURCE_WEISHOP

    if order.get('products'):
        for product_data in order.get('products'):
            product = Product.objects.get(name=product_data.get('name'))
            product.stocks = product.stocks - product_data.get('count')
            product.save()

            model = product_data.get('model', None)
            model_name = get_product_model_keys(model)
            # TODO wan shan gui ge
            # if model:
            #     value = ProductModelPropertyValue.objects.get(name=model)
            #     model_name = '%s:%s' % (value.property_id, value.id)
            # else:
            #     model_name = 'standard'

            product_model = ProductModel.objects.get(product_id=product.id, name=model_name)

            count = product_data.get('count', None)
            if not count:
                count = 1
            count = int(count)

            order_model.product_price += product_model.price * count

            OrderHasProduct.objects.create(
                order=order_model,
                product=product,
                product_name=product.name,
                product_model_name=model_name,
                price=product_model.price,
                total_price=product_model.price * count,
                number=count
            )
            # else:
            # OrderHasProduct.objects.create(
            # order=order_model,
            # product=product,
            # product_name=product.name,
            # product_model_name='standard',
            # price=product.price,
            # 		total_price=product.price,
            # 		number=product_data.get('count')
            # 	)
    order_model.final_price = order_model.product_price
    order_model.save()
    if order.get('integral'):
        member.integral = member.integral - order.get('integral')
        member.save()


def _get_paytype_by_name(payment_name):
    for i in PAYTYPE2NAME:
        if PAYTYPE2NAME[i] == payment_name:
            return i
    return -1


def _get_type_by_name(type_name):
    for i in ORDER_TYPE2TEXT:
        if ORDER_TYPE2TEXT[i] == type_name:
            return i
    return 0


def _get_status_by_name(status_name):
    for i in STATUS2TEXT:
        if STATUS2TEXT[i] == status_name:
            return i
    return 0


def get_model_property_from_web_page(context, property_name):
    model_property = ProductModelProperty.objects.get(
        owner_id=context.webapp_owner_id,
        name=property_name, is_deleted=False)
    url = '/mall2/model_property_list/'
    response = context.client.get(url)
    actual = {}
    model_properties = response.context['model_properties']
    model_property = filter(
                            lambda x: x.id == model_property.id,
                            model_properties)[0]
    actual['name'] = model_property.name
    actual['type'] = u'图片' if model_property.type == PRODUCT_MODEL_PROPERTY_TYPE_IMAGE else u'文字'
    actual['values'] = []
    property_values = ProductModelPropertyValue.objects.filter(
        property_id=model_property.id,
        is_deleted=False)
    for property_value in property_values:
        actual['values'].append({
            "name": property_value.name,
            "image": property_value.pic_url
        })

    return actual
#########################################
# order相关
#########################################


def get_pay_interface(owner_id,type):
    try:
        return PayInterface.objects.get(owner_id=owner_id, type=type)
    except:
        return None


def get_area_ids(areas=None):
    if not areas:
        areas = '北京市 北京市 海淀区'
    areas = areas.replace(',', ' ').split(' ')
    if len(areas) > 0:
        pros = Province.select().dj_where(
            name = areas[0]
        )
        pro_count = pros.count()
        if pro_count == 0:
            province = Province.create(
                name = areas[0]
            )
            pro_id = province.id
        else:
            pro_id = pros[0].id
        ship_area = str(pro_id)
    if len(areas) > 1:
        cities = City.select().dj_where(
            name = areas[1]
        )
        city_count = cities.count()
        if city_count == 0:
            city = City.create(
                name=areas[1],
                zip_code = '',
                province_id = pro_id
            )
            city_id = city.id
        else:
            city_id = cities[0].id
        ship_area = ship_area + '_' + str(city_id)
    if len(areas) > 2:
        dis = District.select().dj_where(
            name = areas[2]
        )
        dis_count = dis.count()
        if dis_count == 0:
            district = District.create(
                name = areas[2],
                city_id = city_id
            )
            ship_area = ship_area + '_' + str(district.id)
        else:
            ship_area = ship_area + '_' + str(dis[0].id)
    return ship_area