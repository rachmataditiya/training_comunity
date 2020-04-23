from odoo import models
from ..exceptions import RestException


class Product(models.Model):
    _inherit = 'product.product'

    def api_get_product(self, product_id=False):
        read_list = [
            'write_date',
            'name',
            'type',
            'default_code'
        ]
        if product_id:
            product_ids = self.browse(product_id)
            result = product_ids.read(read_list, load=False)
            return result, len(product_ids.exists())
        search_list = [
            ('active', '=', True)]
        product_ids = self.search(search_list)
        result = product_ids.read(read_list, load=False)
        return result

class ProductCategory(models.Model):
    _inherit = 'product.category'

    def api_get_category(self, category_id=False):
        read_list = [
            'write_date',
            'id',
            'name',
            'parent_id'
        ]
        if category_id:
            category_ids = self.browse(category_id)
            result = category_ids.read(read_list, load=False)
            return result, len(category_ids.exists())
        search_list = []
        category_ids = self.search(search_list)
        result = category_ids.read(read_list, load=False)
        return result