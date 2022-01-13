# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    ora_check_number = fields.Char(string='Check Number')
    