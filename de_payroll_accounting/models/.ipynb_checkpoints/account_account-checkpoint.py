# -*- coding: utf-8 -*-

from odoo import models, fields, api, _



class AccountAccounts(models.Model):
    _inherit = 'account.account'
    
    
    
    controlled_id = fields.Many2one('controlled.account', string='Controlled Account')
    salary_rule_id = fields.Many2many('hr.salary.rule', string='Salary Rule')

    
    
    
    
    
