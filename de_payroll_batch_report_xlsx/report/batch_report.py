# -*- coding: utf-8 -*-

import json
from odoo import models
from odoo.exceptions import UserError


class BatchPayslip(models.Model):
    _name = 'report.de_payroll_batch_report_xlsx.batch_payslip_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        data = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
        format1 = workbook.add_format({'font_size': '12', 'align': 'left', 'bold': True})
        format_right = workbook.add_format({'font_size': '12', 'align': 'right'})
        format_left = workbook.add_format({'font_size': '12', 'align': 'left'})
        format_total = workbook.add_format({'font_size': '12', 'align': 'right', 'bold': True,'border': True})
        sheet1 = workbook.add_worksheet('Summary Report')
        sheet2 = workbook.add_worksheet('Details Report')
        bold = workbook. add_format({'bold': True, 'align': 'center','border': True})
        sr_no = 1
        row = 1
        
        sheet1.write(0, 0, 'Sr.#', format1)
        sheet1.write(0, 1, 'EMP', format1)
        sheet1.write(0, 2, 'Name', format1)
        sheet1.write(0, 3, 'Bank Account', format1)
        sheet1.write(0, 4, 'Net Payable', format1)
        sheet1.set_column(0, 1, 5)
        sheet1.set_column(2, 2, 25)
        sheet1.set_column(3, 3, 22)
        sheet1.set_column(4, 4, 13)
        total_net_payable = 0
        payslips=self.env['hr.payslip'].search([('payslip_run_id','=',lines.id)])
        extra_payroll_rule= self.env['hr.salary.rule'].search([('detail_report','=',True),('detail_deduction','!=',True),('detail_compansation','!=',True)], order='detail_sequence asc')

        deduction_rule= self.env['hr.salary.rule'].search([('detail_deduction','=',True)], order='detail_sequence asc')
        compansation_rule= self.env['hr.salary.rule'].search([('detail_compansation','=',True)], order='detail_sequence asc')
        deduction_rule_list=[]
        compansation_rule_list=[]
        extra_rule_list=[]
        
        for extra_rule in extra_payroll_rule:
            extra_rule_amount=0
            for extra_slip in payslips:
                for extra_slip_rule in extra_slip.line_ids:
                    if extra_slip_rule.salary_rule_id.id==extra_rule.id:
                        extra_rule_amount +=   extra_slip_rule.amount  
                        
            if extra_rule_amount !=0:
                extra_rule_list.append(extra_rule.id)
        
        for comp_rule in compansation_rule:
            comp_rule_amount=0
            for compansation_slip in payslips:
                for compansation_rule in compansation_slip.line_ids:
                    if compansation_rule.salary_rule_id.id==comp_rule.id:
                        comp_rule_amount +=   compansation_rule.amount  
                        
            if comp_rule_amount !=0:
                compansation_rule_list.append(comp_rule.id)
                
        for ded_rule in deduction_rule:
            ded_rule_amount=0
            for ded_slip in payslips:
                for deduction_rule in ded_slip.line_ids:
                    if deduction_rule.salary_rule_id.id==ded_rule.id:
                        ded_rule_amount +=   deduction_rule.amount  
                        
            if ded_rule_amount !=0:
                deduction_rule_list.append(ded_rule.id)  
         
        uniq_compansation_rule_list = set(compansation_rule_list)   
        uniq_deduction_rule_list = set(deduction_rule_list) 
        uniq_extra_rule_list = set(extra_rule_list) 
        uniq_deduction_rule= self.env['hr.salary.rule'].search([('id','in',list(uniq_deduction_rule_list))], order='detail_sequence asc')
        uniq_compansation_rule= self.env['hr.salary.rule'].search([('id','in',list(uniq_compansation_rule_list))], order='detail_sequence asc')
        uniq_extra_rule= self.env['hr.salary.rule'].search([('id','in',list(uniq_extra_rule_list))], order='detail_sequence asc')
            
        for slip in payslips:
            net_payable = 0
            for rule_line in slip.line_ids:
                if rule_line.code=='NET':
                    net_payable = rule_line.amount    
            sheet1.write(row, 0, sr_no, format_right)
            sheet1.write(row, 1, str(slip.employee_id.emp_number.lstrip('0') if slip.employee_id.emp_number else '-'), format_right)
            sheet1.write(row, 2, str(slip.employee_id.name), format_left)
            sheet1.write(row, 3, str(slip.employee_id.bank_account_id.acc_number if slip.employee_id.bank_account_id.acc_number else '-'), format_right)
            sheet1.write(row, 4, str('{0:,}'.format(int(round(net_payable)))), format_right)
            total_net_payable +=round(net_payable)
            row +=1
            sr_no += 1
        row +=1    
        sheet1.write(row, 0, ' ', format_right)
        sheet1.write(row, 1, ' ', format_right)
        sheet1.write(row, 2, ' ', format_left)
        sheet1.write(row, 3, ' ', format_right)
        sheet1.write(row, 4, str('{0:,}'.format(int(round(total_net_payable)))), format_total) 
        
        sheet2_row=1
        sheet2.write(0, 0, 'SR#', format1)
        sheet2.write(0, 1, 'Period', format1)
        sheet2.write(0, 2, 'Cc', format1)
        sheet2.write(0, 3, 'Ccd', format1)
        sheet2.write(0, 4, 'Location', format1)
        sheet2.write(0, 5, 'Dept Name', format1)
        sheet2.write(0, 6, 'Emp', format1)
        sheet2.write(0, 7, 'Name', format1)
        sheet2.write(0, 8, 'Doj', format1)
        sheet2.write(0, 9, 'Dob', format1)
        sheet2.write(0, 10, 'Position', format1)
        sheet2.write(0, 11, 'Grade', format1)
        sheet2.write(0, 12, 'Grade Type', format1)
        sheet2.write(0, 13, 'Emp Type', format1)
        sheet2.write(0, 14, 'Nic No', format1)
        sheet2.write(0, 15, 'Bank Account', format1)
        sheet2.write(0, 16, 'Bank Name', format1)
        sheet2.write(0, 17, 'Base Salary', format1)
        sheet2.write(0, 18, 'Days', format1)
        sheet2.set_column(0, 0, 5)
        sheet2.set_column(1, 1, 10)
        sheet2.set_column(2, 2, 5)
        sheet2.set_column(3, 3, 20)
        sheet2.set_column(4, 5, 10)
        sheet2.set_column(6, 6, 5)
        sheet2.set_column(7, 7, 20)
        sheet2.set_column(8, 9, 10)
        sheet2.set_column(10, 10, 20)
        sheet2.set_column(11, 12, 10)
        sheet2.set_column(13, 13, 15)
        sheet2.set_column(12, 12, 13)
        sheet2.set_column(14, 17, 15)
        sheet2.set_column(18, 18, 5)
        sheet2.set_column(19, 50, 20)
        extra_col = 19
        for extra in uniq_extra_rule:
            sheet2.write(0, extra_col, str(extra.detail_label), format1)
            extra_col += 1
            
        comp_col = extra_col
        for comp in uniq_compansation_rule:
            sheet2.write(0, comp_col, str(comp.detail_label), format1)
            comp_col += 1
            
        sheet2.write(0, comp_col, 'Total', format1)
        comp_col += 1
        ded_col = comp_col
        for ded in uniq_deduction_rule:
            sheet2.write(0, ded_col, str(ded.detail_label), format1)
            ded_col += 1
        sheet2.write(0, ded_col, 'Tot.Ded', format1)
        ded_col += 1
        sheet2.write(0, ded_col, 'Net Payable', format1)
        
        sheet2_sr_no = 1
        total_net_payable_sheet2 = 0
        grand_total_compansation_amount = 0
        grand_total_deduction_amount = 0
        for slip in payslips:
            cost_center = '-'
            cost_account = '-'
            absent_days = 0
            net_payable_sheet2 = 0
            for sheet2_rule_line in slip.line_ids:
                if sheet2_rule_line.code=='NET':
                    net_payable_sheet2 = sheet2_rule_line.amount     
            fiscal_month = self.env['fiscal.year.month'].search([('id','=', slip.date_to.month)], limit=1)
            working_days= fiscal_month.days   
            for workday in slip.worked_days_line_ids:
                if workday.work_entry_type_id.code == "ABSENT100":
                    absent_days += workday.number_of_days
            payable_days =  (working_days - absent_days) 
            if slip.employee_id.leave_ded==True:
                payable_days = working_days        
            contract = self.env['hr.contract'].search([('employee_id','=',slip.employee_id.id),('state','=','open')], limit=1)  
            for cost_line in contract.cost_center_information_line:
                cost_account = cost_line.cost_center.name
                cost_center = cost_line.cost_center.code   
            sheet2.write(sheet2_row, 0, sheet2_sr_no, format_right)
            sheet2.write(sheet2_row, 1, str(slip.date_to.strftime('%b-%y')), format_left)
            sheet2.write(sheet2_row, 2, str(cost_center), format_right)
            sheet2.write(sheet2_row, 3, str(cost_account), format_right)
            sheet2.write(sheet2_row, 4, str(slip.employee_id.work_location_id.name if slip.employee_id.work_location_id else '-'), format_left)
            sheet2.write(sheet2_row, 5, str(slip.employee_id.department_id.name if slip.employee_id.department_id else '-'), format_left)
            sheet2.write(sheet2_row, 6, str(slip.employee_id.emp_number.lstrip('0') if slip.employee_id.emp_number else '-'), format_right)
            sheet2.write(sheet2_row, 7, str(slip.employee_id.name), format_left)
            sheet2.write(sheet2_row, 8, str(slip.employee_id.date.strftime("%d-%b-%y") if slip.employee_id.date else '-'), format_right)
            sheet2.write(sheet2_row, 9, str(slip.employee_id.birthday.strftime("%d-%b-%y") if slip.employee_id.birthday else '-'), format_right)
            sheet2.write(sheet2_row, 10, str(slip.employee_id.job_id.name if slip.employee_id.job_id else '-'), format_left)
            sheet2.write(sheet2_row, 11, str(slip.employee_id.grade_designation.name if slip.employee_id.grade_designation else '-'), format_left)
            sheet2.write(sheet2_row, 12, str(slip.employee_id.grade_type.name if slip.employee_id.grade_type.name else '-'), format_left)
            sheet2.write(sheet2_row, 13, str(slip.employee_id.emp_type if slip.employee_id.emp_type else '-'), format_left)
            sheet2.write(sheet2_row, 14, str(slip.employee_id.cnic if slip.employee_id.cnic else '-'), format_right)
            sheet2.write(sheet2_row, 15, str(slip.employee_id.bank_account_id.acc_number if slip.employee_id.bank_account_id.acc_number else '-'), format_right)
            sheet2.write(sheet2_row, 16, str(slip.employee_id.bank_account_id.bank_id.name if slip.employee_id.bank_account_id.bank_id else '-'), format_left)
            sheet2.write(sheet2_row, 17, str('{0:,}'.format(int(round(contract.wage)))), format_right)
            sheet2.write(sheet2_row, 18, str(round(payable_days,1)), format_right)
            
            sheet2_extra_col = 19
            for extra_value in uniq_extra_rule:
                extra_amount = 0
                for sheet2_extra_rule in slip.line_ids:
                    if extra_value.id == sheet2_extra_rule.salary_rule_id.id:
                        extra_amount += sheet2_extra_rule.amount     
                sheet2.write(sheet2_row, sheet2_extra_col, str('{0:,}'.format(int(round(extra_amount))) if extra_amount !=0 else '-'), format_right) 
                sheet2_extra_col +=1
            
            sheet2_comp_col = sheet2_extra_col
            total_compansation_amount = 0
            total_deduction_amount = 0
            for comp_value in uniq_compansation_rule:
                comp_amount = 0
                for sheet2_rule in slip.line_ids:
                    if comp_value.id == sheet2_rule.salary_rule_id.id:
                        comp_amount += sheet2_rule.amount     
                sheet2.write(sheet2_row, sheet2_comp_col, str('{0:,}'.format(int(round(comp_amount))) if comp_amount !=0 else '-'), format_right)
                total_compansation_amount += comp_amount
                sheet2_comp_col += 1
            sheet2.write(sheet2_row, sheet2_comp_col, str('{0:,}'.format(int(round(total_compansation_amount)))), format_right)
            grand_total_compansation_amount +=round(total_compansation_amount)
            sheet2_comp_col += 1
            sheet2_ded_col = sheet2_comp_col
            for ded_value in uniq_deduction_rule:
                ded_amount = 0
                for sheet2_ded_rule in slip.line_ids:
                    if ded_value.id == sheet2_ded_rule.salary_rule_id.id:
                        ded_amount += sheet2_ded_rule.amount
                sheet2.write(sheet2_row, sheet2_ded_col, str('{0:,}'.format(int(round(ded_amount))) if ded_amount !=0 else '-'), format_right)
                total_deduction_amount += ded_amount
                sheet2_ded_col += 1
            sheet2.write(sheet2_row, sheet2_ded_col, str('{0:,}'.format(int(round(total_deduction_amount)))), format_right)
            grand_total_deduction_amount +=round(total_deduction_amount)
            sheet2_ded_col += 1            
            sheet2.write(sheet2_row, sheet2_ded_col, str('{0:,}'.format(int(round(net_payable_sheet2)))), format_right)
            total_net_payable_sheet2 +=round(net_payable_sheet2)
            sheet2_sr_no += 1
            sheet2_row += 1
            
        sheet2_row += 1
        sheet2.write(sheet2_row, 0, str(), format1)
        sheet2.write(sheet2_row, 1, str(), format1)
        sheet2.write(sheet2_row, 2, str(), format1)
        sheet2.write(sheet2_row, 3, str(), format1)
        sheet2.write(sheet2_row, 4, str(), format1)
        sheet2.write(sheet2_row, 5, str(), format1)
        sheet2.write(sheet2_row, 6, str(), format1)
        sheet2.write(sheet2_row, 7, str(), format1)
        sheet2.write(sheet2_row, 8, str(), format1)
        sheet2.write(sheet2_row, 9, str(), format1)
        sheet2.write(sheet2_row, 10, str(), format1)
        sheet2.write(sheet2_row, 11, str(), format1)
        sheet2.write(sheet2_row, 12, str(), format1)
        sheet2.write(sheet2_row, 13, str(), format1)
        sheet2.write(sheet2_row, 14, str(), format1)
        sheet2.write(sheet2_row, 15, str(), format1)
        sheet2.write(sheet2_row, 16, str(), format1)
        sheet2.write(sheet2_row, 17, str(), format1)
        sheet2.write(sheet2_row, 18, str(), format1)
        
        grand_total_compansation_amount_list = []
        grand_total_deduction_amount_list = []
        grand_extra_total_amount_list = []
        
        for grand_extra_rule in uniq_extra_rule:
            grand_extra_total_amount = 0
            for slip in payslips:
                for slip_extra_rule in slip.line_ids:
                    if  slip_extra_rule.salary_rule_id.id==grand_extra_rule.id:
                        grand_extra_total_amount += slip_extra_rule.amount
            grand_extra_total_amount_list.append(grand_extra_total_amount)  

        for grand_ded_rule in uniq_deduction_rule:
            grand_ded_total_amount = 0
            for slip in payslips:
                for slip_rule in slip.line_ids:
                    if  slip_rule.salary_rule_id.id==grand_ded_rule.id:
                        grand_ded_total_amount += slip_rule.amount
            grand_total_deduction_amount_list.append(grand_ded_total_amount)  
            
        for grand_rule in uniq_compansation_rule:
            grand_compansation_total_amount = 0
            for ded_slip in payslips:
                for ded_rule in ded_slip.line_ids:
                    if  ded_rule.salary_rule_id.id==grand_rule.id:
                        grand_compansation_total_amount += ded_rule.amount    
            grand_total_compansation_amount_list.append(grand_compansation_total_amount) 
        grand_extra_col = 19 
        for grand_extra in grand_extra_total_amount_list:
            sheet2.write(sheet2_row, grand_extra_col, str('{0:,}'.format(int(round(grand_extra)))), format_total)
            grand_extra_col += 1
        grand_comp_col = grand_extra_col
        for grand_comp in grand_total_compansation_amount_list:
            sheet2.write(sheet2_row, grand_comp_col, str('{0:,}'.format(int(round(grand_comp)))), format_total)
            grand_comp_col += 1
            
        sheet2.write(sheet2_row, grand_comp_col, str('{0:,}'.format(int(round(grand_total_compansation_amount)))), format_total)
        grand_comp_col += 1
        grand_ded_col = grand_comp_col
        for grand_ded in grand_total_deduction_amount_list:
            sheet2.write(sheet2_row, grand_ded_col, str('{0:,}'.format(int(round(grand_ded)))), format_total)
            grand_ded_col += 1
        sheet2.write(sheet2_row, grand_ded_col, str('{0:,}'.format(int(round(grand_total_deduction_amount)))), format_total)
        grand_ded_col += 1
        sheet2.write(sheet2_row, grand_ded_col, str('{0:,}'.format(int(round(total_net_payable_sheet2)))), format_total)   
        
        
            
            
            