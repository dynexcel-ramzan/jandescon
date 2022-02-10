# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ORAFiscalYear(models.Model):
    _name = 'ora.fiscal.year'
    _description = 'ORA Fiscal Year'

    name = fields.Char(string='Name')

    
class HrEmployee(models.Model):
    _inherit = 'hr.employee' 
    
    
    retirement_date = fields.Date(string='Retirement Date')
    retirement_age = fields.Integer(string='Retirement Age')