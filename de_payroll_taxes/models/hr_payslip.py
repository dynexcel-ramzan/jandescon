# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import date, datetime, timedelta

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    is_salary_Stop = fields.Boolean(string='Stop Salary')
    current_month_tax_amount = fields.Float(string='Tax Amount')
    arrears_amount = fields.Float(string='Arrears Amount')
    current_pfund = fields.Float(string='Pfund Amount')
    absent_amount = fields.Float(string='Absent Amount')
    ot_hours = fields.Float(string='OT Hours')
    fiscal_month = fields.Many2one('fiscal.year.month', string='Month')
    tax_year = fields.Char(string='Year')
    next_fiscal_month = fields.Date(string='Next Month')
    net_work_days = fields.Float(string='Net Days', compute='_compute_net_workdays')

    @api.depends('worked_days_line_ids', 'worked_days_line_ids.number_of_days')
    def _compute_net_workdays(self):
        for slip in self:
            net_days = 0
            absent_days = 0
            for workday in slip.worked_days_line_ids:
                if workday.work_entry_type_id.code == "ABSENT100":
                    absent_days += workday.number_of_days
            net_days = slip.fiscal_month.days - absent_days  
            slip.update({
                'net_work_days': net_days
            })

    def compute_sheet(self):
        for pay in self:
            next_month=pay.date_to +timedelta(31)
            pay.update({
                'fiscal_month':  pay.date_to.month,
                'next_fiscal_month': next_month,
                'tax_year': pay.date_to.year,
            })
            for rule in pay.line_ids:
                if rule.code=='PF01':  
                    pay.update({
                      'current_pfund': rule.amount,
                    })
                if rule.code=='ARR01':  
                    pay.update({
                      'arrears_amount': rule.amount,
                    }) 
                if rule.code=='ABNT':  
                    pay.update({
                      'absent_amount': rule.amount,
                    })     
        rec = super(HrPayslip, self).compute_sheet()
        
        return rec
    
    
    def _action_update_income_tax(self, payslip, date):
        total_allowance_amount = 0
        total_basic_amount = 0
        result = 0
        bonus_amount = 0
        arreas_amount = 0
        before_promotion_fiscal_month = 0
        after_promotion_fiscal_month = 0
        current_year_promotion=self.env['hr.employee.promotion'].search([('employee_id','=',payslip.employee_id.id),('tax_year','=', payslip.tax_year)], limit=1, order='period')
        promotion_month=int(current_year_promotion.period)
        fiscal_year_month=int(payslip.company_id.fiscal_period)
        if payslip.company_id.fiscalyear_last_day>1:
            fiscal_year_month=int(payslip.company_id.fiscal_period) + 1
        before_promotion_fiscal_month = promotion_month - fiscal_year_month
        after_promotion_fiscal_month = 12 - before_promotion_fiscal_month
        if current_year_promotion:
           total_basic_amount =  (before_promotion_fiscal_month * current_year_promotion.previous_wage) + (after_promotion_fiscal_month * current_year_promotion.new_wage)   
        if not current_year_promotion:
            total_basic_amount = payslip.contract_id.wage
        for arreas_input in payslip.input_line_ids:
            if arreas_input.input_type_id.is_arrears == True:
                arreas_amount += arreas_input.amount 
        for bonus_input in payslip.input_line_ids:
            if bonus_input.input_type_id.is_arrears == True:
                bonus_amount += bonus_input.amount        
        rule_categ_list = []
        rule_categories=self.env['hr.salary.rule.category'].search([('is_compute_tax','=',True)])
        for rule_categ in rule_categories:
            rule_categ_list.append(rule_categ.id)                
        for rule_line in payslip.line_ids:
            if rule_line.category_id.id in rule_categ_list:
                total_allowance_amount +=  rule_line.amount        
        pf=0
        if (payslip.employee_id.pf_member == 'yes_with' or payslip.employee_id.pf_member == 'yes_without' and payslip.company_id.id==6): 
            pf=((payslip.contract_id.wage * 9)/100)*12
        elif (payslip.employee_id.pf_member == 'yes_with' or payslip.employee_id.pf_member == 'yes_without' and payslip.company_id.id!=6): 
            pf=((payslip.contract_id.wage * 6.3)/100)*12
        apf=0
        if(pf>150000):
            apf=pf-150000
        if(apf > 0):
            result= apf 
        initial_fiscal_month = 12 
        stop_salary_fiscal_year=0
        payslips = self.env['hr.payslip'].search([('employee_id','=',payslip.employee_id.id),('tax_year','=',payslip.tax_year),('is_salary_Stop','=',True)])
        for paye in payslips:
            stop_salary_fiscal_year += 1   
        fiscal_month = (initial_fiscal_month - stop_salary_fiscal_year)    
        total_gross =  total_basic_amount + total_allowance_amount + arreas_amount + bonus_amount + (apf/fiscal_month)           
        if ((total_gross)*fiscal_month>=600001 and (total_gross)*fiscal_month<=1200000):
            result = (round(((((total_gross*fiscal_month)-600000)/100)*5)/fiscal_month,0))
        elif ((total_gross)*fiscal_month>=1200001 and (total_gross)*fiscal_month<=1800000):
            result = (round((((((categories.GROSS*fiscal_month)-1200000)/100)*10)+30000)/fiscal_month,0))
        elif ((total_gross)*fiscal_month>=1800001 and (total_gross)*fiscal_month<=2500000):
            result = (round((((((total_gross*fiscal_month)-1800000)/100)*15)+90000)/fiscal_month,0))
        elif ((total_gross)*fiscal_month>=2500001 and (total_gross)*fiscal_month<=3500000):
            result = (round((((((total_gross*fiscal_month)-2500000)/100)*17.5)+195000)/fiscal_month,0))
        elif ((total_gross)*fiscal_month>=3500001 and (total_gross)*fiscal_month<=5000000):
            result = (round((((((total_gross*fiscal_month)-3500000)/100)*20)+370000)/fiscal_month,0))
        elif ((total_gross)*fiscal_month>=5000001 and (total_gross)*fiscal_month<=8000000):
            result = (round((((((total_gross*fiscal_month)-5000000)/100)*22.5)+670000)/fiscal_month,0))
        elif ((total_gross)*fiscal_month>=8000001 and (total_gross)*fiscal_month<=12000000):
            result = (round((((((total_gross*fiscal_month)-8000000)/100)*25)+1345000)/fiscal_month,0))
        elif ((total_gross)*fiscal_month>=12000001 and (total_gross)*fiscal_month<=30000000):
            result = (round((((((total_gross*fiscal_month)-12000000)/100)*27.5)+2345000)/fiscal_month,0))
        elif ((total_gross)*fiscal_month>=30000001 and (total_gross)*fiscal_month<=50000000):
            result = (round((((((total_gross*fiscal_month)-30000000)/100)*30)+7295000)/fiscal_month,0))
        elif ((total_gross)*fiscal_month>=50000001 and (total_gross)*fiscal_month<=75000000):
            result = (round((((((total_gross*fiscal_month)-50000000)/100)*32.5)+13295000)/fiscal_month,0))
        elif ((total_gross)*fiscal_month>=75000001):
            result = (round((((((total_gross*fiscal_month)-75000000)/100)*35)+21420000)/fiscal_month,0))
        else:
            result = 0.0  
        tax_credit=self.env['hr.tax.credit'].search([('employee_id','=',payslip.employee_id.id),('tax_year','=',payslip.date_to.strftime('%Y')),('period','=',payslip.date_to.strftime('%m'))], limit=1) 
        tax_credit_amount=0
        if tax_credit:
            tax_credit_amount = tax_credit.tax_amount  
        if   tax_credit_amount >= result:
            result = 0
            tax_credit.update({
                'reconcile_amount': result,
                'remaining_amount': tax_credit_amount - result,
            })
        else:
            result = result - tax_credit_amount
            tax_credit.update({
                'reconcile_amount': tax_credit_amount,
                'remaining_amount': 0,
            })
        payslip.update({
            'current_month_tax_amount': result,
        })

    
    