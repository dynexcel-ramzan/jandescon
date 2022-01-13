# -*- coding: utf-8 -*-

import base64

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips, ResultRules
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    


    def compute_sheet(self):
        for payslip in self:
            res = super(HrPayslip, payslip).compute_sheet()
            for rule in payslip.line_ids:
    #                 rule_code = 'COST1'
                cost_amount = 0
                contract = self.env['hr.contract'].search([('employee_id','=',payslip.employee_id.id),('state','=','open')],limit=1)
                for cost_line in contract.cost_center_information_line:
                    if cost_line.cost_center_id.id == rule.salary_rule_id.analytic_account_id.id:
    #                     rule_code =  cost_line.cost_center_id.code 
    #                     for inner_rule in self.line_ids:
                        if rule.category_id.name in ['Basic','Allowance','Contribution Exp']:
                            cost_amount = (cost_line.percentage_charged / 100) * rule.amount
                            rule.update({
                                'amount': cost_amount,
                                'cost_divided': True
                            })
            for rule in payslip.line_ids:
                if rule.cost_divided == False:
                    contract = self.env['hr.contract'].search([('employee_id','=',payslip.employee_id.id),('state','=','open')],limit=1)
                    for cost_line in contract.cost_center_information_line:

                        if cost_line.cost_center_id.id != rule.salary_rule_id.analytic_account_id.id:
                            if rule.category_id.name in ['Basic','Allowance','Contribution Exp']:
                                rule.update({
                                    'amount': 0
                                })
            for rule in payslip.line_ids:
                if rule.amount == 0.0:
                    rule.unlink()    

            total_basic = 0
            total_allowance = 0
            total_deduction = 0
            total_compensation = 0
            for rule in payslip.line_ids:
                if rule.category_id.name == 'Basic':
                    total_basic = rule.total + total_basic
                if rule.category_id.name == 'Allowance':
                    total_allowance = rule.total + total_allowance
                if rule.category_id.name == 'Deduction':
                    total_deduction = rule.total + total_deduction
                if rule.category_id.name == 'Compensation':
                    total_compensation = rule.total + total_compensation
            for rule in payslip.line_ids:
                if rule.category_id.code == 'GROSS':
                    rule.update({
                        'amount': total_basic + total_allowance + total_compensation
                    })
                if rule.category_id.code == 'NET':
                    rule.update({
                        'amount': total_basic + total_allowance + total_compensation + total_deduction
                    })

            return res



class HrPayslipline(models.Model):
    _inherit = 'hr.payslip.line'
    
    cost_divided = fields.Boolean(String="Cost Divided")

