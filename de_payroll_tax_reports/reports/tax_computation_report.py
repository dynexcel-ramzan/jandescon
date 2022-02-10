# -*- coding: utf-8 -*-
#################################################################################
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-today Dynexcel <www.dynexcel.com>

#################################################################################
import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError

class PayrollTaxComputation(models.AbstractModel):
    _name = 'report.de_payroll_tax_reports.computation_report'
    _description = 'Tax Computation Report'

    '''Find payroll Tax Computation Report between the date'''
    @api.model
    def _get_report_values(self, docids, data=None): 
        docs = self.env['tax.computation.wizard'].browse(self.env.context.get('active_id'))
        payslips=self.env['hr.payslip'].search([('employee_id','=',docs.employee_id.id),('date_to','>=',docs.date_from),('date_to','<=',docs.date_to)], order='date_to asc')
        salary_rules=self.env['hr.salary.rule'].search([('computation_report','=',True)], order='computation_sequence asc')
        pfund_rule=self.env['hr.salary.rule'].search([('pfund_amount','=',True)], limit=1) 
        contract=self.env['hr.contract'].search([('employee_id','=',docs.employee_id.id),('state','=','open')], limit=1)

        pfund_amount = round((contract.wage/12))
        total_amount_list=[]
        tax_rebate_detail=[]
        
        for rule in salary_rules:
            total_amount=0
            for payslip in payslips:
                for rule_line in payslip.line_ids:
                    if rule.id==rule_line.salary_rule_id.id:
                        total_amount += rule_line.amount
                    if pfund_rule.id==rule_line.salary_rule_id.id:
                        pfund_amount = rule_line.amount    
            total_amount_list.append({
                'amount': round(total_amount)
            })   
        ppfund_amount=0     
        for slip in payslips: 
            tax_credit=self.env['hr.tax.credit'].search([('employee_id','=', slip.employee_id.id),('tax_year','=', slip.date_to.strftime('%Y'))])
            loan_amount = 0
            loan_name = ''
            for rule in slip.line_ids:
                if pfund_rule.id == rule.salary_rule_id.id:
                    ppfund_amount =  rule.amount   
                if rule.code in ('LOAN', 'SLO01'):
                    loan_amount =  rule.amount 
                    loan_name = rule.name
            if tax_credit and loan_amount > 0:
                tax_rebate_detail.append({
                    'name':   tax_credit.name,
                    'period': slip.date_to.strftime('%b-%y'),
                    'amount_credit':  0,
                    'tax_credit':   tax_credit.tax_amount,
                    'loan_amount':  loan_amount,
                })
            elif tax_credit:
                tax_rebate_detail.append({
                    'name':   tax_credit.name,
                    'period': slip.date_to.strftime('%b-%y'),
                    'amount_credit':  0,
                    'tax_credit':   tax_credit.tax_amount,
                    'loan_amount':  0,
                })
            elif loan_amount >0:
               tax_rebate_detail.append({
                    'name':   loan_name,
                    'period': slip.date_to.strftime('%b-%y'),
                    'amount_credit':  0,
                    'tax_credit':   tax_credit.tax_amount,
                    'loan_amount':  loan_amount,
                }) 
            
        tax_range=self.env['hr.tax.range.line'].search([('year','=',docs.date_to.year)])
        if payslips:             
            if (docs.employee_id.pf_member == 'yes_with' or docs.employee_id.pf_member == 'yes_without' and docs.employee_id.company_id.id==6): 
                pf=((contract.wage * 9)/100)*12
            elif (docs.employee_id.pf_member == 'yes_with' or docs.employee_id.pf_member == 'yes_without' and docs.employee_id.company_id.id!=6): 
                pf=((contract.wage * 6.3)/100)*12
            apf=0
            if docs.employee_id.id==3630:
                pf=(((contract.wage * 6.3)/100)*11 ) + 19054
            if(pf>150000):
                pfund_amount=pf-150000
                exceed_limit = True 
 
            return {
                'docs': docs,
                'payslips': payslips,
                'exceed_limit': exceed_limit,
                'pfund_amount': pfund_amount,
                'salary_rules': salary_rules,
                'total_amount_list': total_amount_list,
                'tax_rebate_detail': tax_rebate_detail,
                'tax_range': tax_range,
            }
        else:
            raise UserError("There is not any Payslips in between selected dates")