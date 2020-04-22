from odoo import http
from odoo.http import request, route

from ..jwt.login import token_required

class ApiPartner(http.Controller):

    @route(route=['/api/v1/customer/',
                  '/api/v1/customer/<int:partner_id>'],
           methods=['GET'], type='json', auth='public', csrf=False)
    @token_required()
    def get_customer(self, partner_id=False, debug=False, **kwargs):
        partner = request.env['res.partner'].with_user(
            kwargs.get('uid', 1)).api_get_partner(partner_id=partner_id)
        result = {}
        result['result'] = partner
        return result
