# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

    

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    expense_advance_id = fields.Many2one('advance.against.expense', string='Advance Against Expense')
    
   