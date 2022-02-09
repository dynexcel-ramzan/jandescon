# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2022-today Dynexcel Business Solution <www.dynexcel.com>

#################################################################################

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError

class PayrollReconciliation(models.AbstractModel):
    _name = 'report.de_payroll_reconcilation_report.reconcilation_report'
    _description = 'Reconciliation Wizard'

    '''Find payroll reconcilation between the date'''
    @api.model
    def _get_report_values(self, docids, data=None):
        deduction_list = []
        compansation_list = []
        docs = self.env['reconciliation.wizard'].browse(self.env.context.get('active_id'))
        previous_employees = 0
        previous_net_amount = 0
        current_employees = 0
        current_net_amount = 0
        deduction_rule_list = []
        compansation_rule_list = []
        deduction_rule_list=self.env['hr.salary.rule'].search([('reconcile_deduction','=',True)]).ids
        compansation_rule_list=self.env['hr.salary.rule'].search([('reconcile_compansation','=',True)]).ids
        previous_month_payslips = self.env['hr.payslip'].search([('fiscal_month','=',docs.date_from.month),('company_id','=', docs.company_id.id),('state','!=','cancel')])
        for previous_payslip in previous_month_payslips:
            previous_employees += 1
            for previous_rule in previous_payslip.line_ids:
                if previous_rule.code=='NET':
                    previous_net_amount += previous_rule.amount
                
        current_month_payslips = self.env['hr.payslip'].search([('fiscal_month','=',docs.date_to.month),('company_id','=', docs.company_id.id),('state','!=','cancel')])
        for current_payslip in current_month_payslips:
            current_employees += 1
            for current_rule in current_payslip.line_ids:
                if current_rule.code=='NET':
                    current_net_amount += current_rule.amount
                
        uniq_deduction_rule_list= set(deduction_rule_list)
        uniq_compansation_rule_list= set(compansation_rule_list)
        for  uniq_list in uniq_deduction_rule_list:
            previous_deduction_amount = 0
            current_deduction_amount = 0
            for ded_previous_payslip in previous_month_payslips:
                for ded_previous_rule in ded_previous_payslip.line_ids:
                    if ded_previous_rule.salary_rule_id.id==uniq_list:
                        previous_deduction_amount += ded_previous_rule.amount
            for ded_current_payslip in current_month_payslips:
                for ded_current_rule in ded_current_payslip.line_ids:
                    if ded_current_rule.salary_rule_id.id==uniq_list:
                        current_deduction_amount += ded_current_rule.amount  
            if  (current_deduction_amount) != 0  or (previous_deduction_amount) != 0:         
                deduction_list.append({
                    'name':  self.env['hr.salary.rule'].search([('id','=',uniq_list)]).name,
                    'previous_month_amount':previous_deduction_amount,
                    'current_month_amount': current_deduction_amount
                }) 
        curr_base_salary_amount = 0
        curr_absnet_amount_amount = 0  
        current_month_base_salary=0
        previous_month_base_salary=0
        pre_base_salary_amount = 0
        pre_absnet_amount_amount = 0
        for comp_pre_payslip in previous_month_payslips:
            for comp_pre_rule in comp_pre_payslip.line_ids:
                if comp_pre_rule.code=='BASIC':
                    pre_base_salary_amount += comp_pre_rule.amount
                if comp_pre_rule.code=='ABNT':
                    pre_absnet_amount_amount += comp_pre_rule.amount 
        for comp_curr_payslip in current_month_payslips:
            for comp_curr_rule in comp_curr_payslip.line_ids:
                
                if comp_curr_rule.code=='BASIC':
                    curr_base_salary_amount += comp_curr_rule.amount
                if comp_curr_rule.code=='ABNT':
                    curr_absnet_amount_amount += comp_curr_rule.amount  
        current_month_base_salary =  (curr_base_salary_amount - curr_absnet_amount_amount)
        previous_month_base_salary =  (pre_base_salary_amount - pre_absnet_amount_amount)
        compansation_list.append({
               'name':  'Base Salary',
               'previous_month_amount':previous_month_base_salary,
               'current_month_amount': current_month_base_salary,
        }) 
        for  comp_uniq_list in uniq_compansation_rule_list:
            previous_compansation_amount = 0
            current_compansation_amount = 0
            
           
            for comp_previous_payslip in previous_month_payslips:
                for comp_previous_rule in comp_previous_payslip.line_ids:
                    if comp_previous_rule.salary_rule_id.id==comp_uniq_list:
                        previous_compansation_amount += comp_previous_rule.amount
            for comp_current_payslip in current_month_payslips:
                for comp_current_rule in comp_current_payslip.line_ids:
                    if comp_current_rule.salary_rule_id.id==comp_uniq_list:
                        current_compansation_amount += comp_current_rule.amount  
            if  (current_compansation_amount) != 0 or (previous_compansation_amount) != 0:           
                compansation_list.append({
                 'name':  self.env['hr.salary.rule'].search([('id','=',comp_uniq_list)]).name,
                 'previous_month_amount':previous_compansation_amount,
                 'current_month_amount': current_compansation_amount,
                })     
        if previous_month_payslips and current_month_payslips:
            return {
                'wizarddocs': docs,
                'previous_employees':  previous_employees,
                'previous_net_amount': previous_net_amount,
                'current_employees': current_employees,
                'current_net_amount': current_net_amount,
                'compansation_list': compansation_list,
                'deduction_list': deduction_list,
            }
        else:
            raise UserError("There is not any Payslips in between selected dates")