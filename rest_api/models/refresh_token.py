from odoo import api
from odoo import models, fields

class RefreshToken(models.Model):
    _name = 'refresh.token'
    _description = 'token table'

    name = fields.Char('Token', copy=False)
    user_id = fields.Many2one('res.users', 'User ID')
    state = fields.Selection([('revoked', 'Revoked'), ('granted', 'Granted')], default='granted', copy=False)
