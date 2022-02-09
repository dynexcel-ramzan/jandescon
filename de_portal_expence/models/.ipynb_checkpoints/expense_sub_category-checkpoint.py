# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ExpenseSubCategory(models.Model):
    _name = 'expense.sub.category'
    _description = 'Expense Sub Category'
    
    name = fields.Char(string='Name', required=True)
    company_id  = fields.Many2one('res.company', string='Company')
    ora_category_id = fields.Many2one('ora.expense.category', string='Expense Category', required=True, copy=True)
    ora_unit = fields.Selection(selection=[
            ('amount', 'Amount'),
            ('km', 'Km'),
        ], string='Unit', 
        )
    amount = fields.Float(string='Amount')
    meter_reading = fields.Float(string='Meter Reading')
    is_petty_cash = fields.Boolean(string='Petty Cash')
   