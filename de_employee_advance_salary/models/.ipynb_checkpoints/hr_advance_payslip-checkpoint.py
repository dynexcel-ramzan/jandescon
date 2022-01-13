# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models,api


class SalaryRuleInput(models.Model):
    _inherit = 'hr.payslip'


    
    
    
    def compute_sheet(self):
        for payslip in self:
            amount = 0 
            adv_salary = self.env['salary.advance'].search([('employee_id', '=', payslip.employee_id.id),
                                                            ('state', '=', 'approve')])

            if adv_salary:
                for adv_obj in adv_salary:
                    current_date = datetime.strptime(str(payslip.date_from), '%Y-%m-%d').date().month
                    adv_date = adv_obj.date
                    existing_date = datetime.strptime(str(adv_date), '%Y-%m-%d').date().month
                    if current_date == existing_date:
                        amount = adv_obj.advance

                        input_exists = self.env['hr.payslip.input'].search([('payslip_id', '=', payslip.id), ('code', '=', 'SAR')])

                        if not input_exists:
                            input_type_exists = self.env['hr.payslip.input.type'].search([('code', '=', 'SAR')])

                            input_exists.create({
                                'input_type_id': input_type_exists.id,
                                'code': 'SAR',
                                'amount': amount,
                                'contract_id': payslip.contract_id.id,
                                'payslip_id': payslip.id,
                            })
                        else:
                            input_exists.write({
                                'amount': amount,
                            })
        rec = super(SalaryRuleInput, self).compute_sheet()
        return rec
            
    
    
    
    
    