# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CostInformationLine(models.Model):
    _inherit = 'cost.information.line'
    
    
    controlled_id = fields.Many2one('controlled.account', string='Controlled Account')
    by_default = fields.Boolean(string='By Default')
    
    
