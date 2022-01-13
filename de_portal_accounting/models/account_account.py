# -*- coding: utf-8 -*-

from odoo import models, fields, api, _





class AccountAccount(models.Model):
    _inherit = 'account.account'
   

    is_publish = fields.Boolean(string="Publish At Website")
    publish_name = fields.Char('Publish Name')

    
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    