# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime
import base64

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval

class HrLoanType(models.Model):
    _name = 'hr.loan.type'
    _description = 'This is loan type'
    _inherit = ['portal.mixin', 'mail.thread']
    
    
    def _default_get_installment(self):
        if self.compansation == 'normal':
            self.installment = 12
        elif self.compansation != 'normal':
            self.installment = 48
            
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    payment_method = fields.Selection([
                                     ('payslip','Payslip'),
                                     ('other','Non Refundable'),
                                      ],  default = 'payslip', string="Payment Method")
    compansation = fields.Selection([
                                     ('normal','Normal'),
                                     ('pfun_refund','PFUND Refundable'),
                                     ('pfund_non_refund','PFUND Non Refundable'),
                                      ],  default = 'normal', string="Conpansation", required=True)
    
    loan_type_proof_ids = fields.One2many('hr.loan.type.proof', 'loan_type_id' , string="Loan Type")
    installment = fields.Integer(string="Installment", required=True, default=_default_get_installment)
    employee_ids = fields.Many2many('hr.employee', string="Employee Info")
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

    employee_category_ids = fields.Many2many('hr.employee.category', string="Employee Category")

    
    @api.model
    def default_get(self, default_fields):
        # OVERRIDE
        values = super(HrLoanType, self).default_get(default_fields)
        proof_data = []
        proof_list = self.env['hr.loan.proof'].search([])
        for proof in proof_list:
            proof_data.append((0,0,{
                'name':  proof.name,
                'mandatory': proof.mandatory,
            })) 
        values['loan_type_proof_ids'] = proof_data       
        return values
    
    
class HrLoanTypeProof(models.Model):
    _name = 'hr.loan.type.proof'
    _description = 'This is loan type proof' 
    
    name = fields.Char(string="Name", readonly=True)
    mandatory = fields.Boolean(string="Mandatory")
    loan_type_id = fields.Many2one('hr.loan.type', string="Loan Type")
    
    