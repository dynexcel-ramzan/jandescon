# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    category_id = fields.Many2one('approval.category', string="Category", required=True)
   
 