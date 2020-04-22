from odoo import models
from ..exceptions import RestException


class Product(models.Model):
    _inherit = 'product.product'

    def api_get_product(self, product_id=False):
        read_list = [
            'write_date',
            'name',
            'street',
            'street2',
            'city',
            'phone',
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