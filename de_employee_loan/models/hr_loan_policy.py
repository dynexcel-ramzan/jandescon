# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime
import base64

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips, ResultRules
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval

class HrLoanPolicy(models.Model):
    _name = 'hr.loan.policy'
    _description = 'This is loan policy'
    _inherit = ['portal.mixin', 'mail.thread']
    
    name = fields.Char(string="Name", required=True)
    policy_type = fields.Selection([
                             ('max_loan','Max loan amount'),
                             ('gap_between_date','Gap between two loans'),
                             ('qualify_period','Qualifying Period'), 
                            ],  default = 'max_loan', string="Policy Type")
    
    value_type = fields.Selection([
                             ('fix_amount', 'Fix Amount'),
                             ('percent', 'Percentage'),
                            ],  default = 'fix_amount', string="Basis")
    
    value = fields.Float(string="Value")
    
    employee_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('contractor', 'Contractor'),
        ('freelancer', 'Freelancer'),
        ('inter', 'Intern'),
        ('part_time', 'Part Time'),
        ('project_based', 'Project Based Hiring'),
        ('outsource', 'Outsource'),
        ], string='Employee Type', index=True, copy=False, default='permanent', track_visibility='onchange')
    
    grade_type_id = fields.Many2one('grade.type', string='Grade Type')
    
    gap_type = fields.Selection([
                             ('year', 'Year'),
                            ],  default = 'year', string="By")
    gap_value = fields.Integer(string="Value")
    
    
    
    
    employee_category_ids = fields.Many2many('hr.employee.category', string="Employee Category")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    employee_ids = fields.Many2many('hr.employee', string="Employee Info")
    
    
    @api.model
    def _create_employee_loan_policy(self):
        if self.employee_ids:
            employee_policy = []
            employee_policy.append((0,0,{
                'name': self.name,
                'code' : self.code,
                'value' : self.value,
                'company_id' : self.company_id,
            }))
            for employee in self.employee_ids:
                employee.update({
                   'loan_policy_ids': employee_policy
                })
    
    
    
    
    
    
    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        if self.employee_ids:
            employee_policy = []
            employee_policy.append((0,0,{
                'name': self.name,
                'code' : self.code,
                'value' : self.value,
                'company_id' : self.company_id,
            }))
            for employee in self.employee_ids:
                employee.update({
                   'loan_policy_ids': employee_policy
                })    
        
        rslt = super(HrLoanPolicy, self).create(vals_list)
        
        return rslt
    
    
    
    
                
    
    

    
    