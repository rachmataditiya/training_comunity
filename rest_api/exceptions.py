from odoo import exceptions

class RestException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message