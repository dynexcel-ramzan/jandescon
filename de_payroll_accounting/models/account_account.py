# -*- coding: utf-8 -*-

from odoo import models, fields, api, _



class AccountAccounts(models.Model):
    _inherit = 'account.account'        
    
    controlled_id = fields.Many2one('controlled.account', string='Controlled Account')
    salary_rule_id = fields.Many2many('hr.salary.rule', string='Salary Rule')
    grade_type_id = fields.Many2one('grade.type', string='Grade Type')  
    emp_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('contractor', 'Contractor'),
        ('freelancer', 'Freelancer'),
        ('inter', 'Intern'),
        ('part_time', 'Part Time'),
        ('project_based', 'Project Based Hiring'),
        ('outsource', 'Outsource'),
        ], string='Employee Type', index=True, copy=False,)

        
    
    
    
    
