# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrPayslipRunType(models.Model):
    _name = 'hr.payslip.run.type'
    _description = 'Payslip Run Type'
    
    name = fields.Char(string='Name')    
    category_id = fields.Many2one('approval.category', string="Category", required=False)
    
    
    
   