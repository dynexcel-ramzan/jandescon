# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    ora_category_id = fields.Many2one('ora.expense.category', string='Expense Category', required=True, copy=True)
    sub_category_id = fields.Many2one('expense.sub.category', string='Expense Sub-Category', required=True, copy=True)
    controlled_id = fields.Many2one('controlled.account', string='Control-Account', required=True, copy=True)

    meter_reading = fields.Float(string='Meter Reading')
    ora_unit = fields.Selection(selection=[
            ('amount', 'Amount'),
            ('km', 'Km'),
        ], string='Unit', required=True,
        )
    is_special = fields.Boolean(string='Special')
    
    
    @api.onchange('sub_category_id')
    def onchange_category(self):
        for line in self:
            if line.sub_category_id:
                line.update({
                    'meter_reading': line.sub_category_id.meter_reading ,
                    'ora_unit': line.sub_category_id.ora_unit,
                })
    