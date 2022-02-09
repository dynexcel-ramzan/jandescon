# -*- coding: utf-8 -*-

from odoo import models, fields, api, _



class EmployeeBenefit(models.Model):
    _inherit = 'hr.contract'
    
    benefit_line_ids = fields.One2many('hr.employee.payslip.benefit', 'cotract_id',string='Benefit Lines')
    

class EmployeeBenefit(models.Model):
    _name = 'hr.employee.payslip.benefit'
    _description = 'This is Employee Benefit'

    name = fields.Char(string='Name', required=True)
    input_type_id = fields.Many2one('hr.payslip.input.type', string='Payslip Rule', required=True)
    cotract_id = fields.Many2one('hr.contract', string='Contract')
    description = fields.Char(string='Desciption')
    amount = fields.Float(string='Amount', required=True)

