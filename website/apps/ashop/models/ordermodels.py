from shop.models.productmodel import Product as ShopProduct

from shop.models.defaults.bases import BaseOrder
from shop.models.defaults.managers import OrderManager



class Product():
    pass

"""
Custom order model (settings.SHOP_ORDER_MODEL)
add methods for downloadable products
"""
class Order(BaseOrder):
    objects = OrderManager()

    class Meta(object):
        abstract = False
        app_label = 'shop'
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
