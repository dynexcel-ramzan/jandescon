# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    
    
    reconcile_deduction = fields.Boolean(string='Reconcile Deduction')
    reconcile_compansation = fields.Boolean(string='Reconcile Compansation')
    
