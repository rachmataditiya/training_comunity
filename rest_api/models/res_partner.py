from odoo import models
from ..exceptions import RestException


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def api_get_partner(self, partner_id=False):
        read_list = [
            'write_date',
            'name',
            'street',
            'street2',
            'city',
            'phone',
        ]
        if partner_id:
            partner_ids = self.browse(partner_id)
            result = partner_ids.read(read_list, load=False)
            return result, len(partner_ids.exists())
        search_list = [
            ('active', '=', True)]
        partner_ids = self.search(search_list)
        result = partner_ids.read(read_list, load=False)
        return result