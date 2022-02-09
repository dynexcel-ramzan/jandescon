# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError



class Hr(models.Model):
    _inherit = 'hr.payslip'
    
    
    
    def action_generate_entry(self):
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        for payslip in self:
            contract=self.env['hr.contract'].search([('employee_id','=',payslip.employee_id.id),('state','=','open')], limit=1)   
            move_dict = {
                  'name': payslip.name,
                  'journal_id': payslip.journal_id.id,
                  'date': payslip.date_to,
                  'partner_id': payslip.employee_id.address_home_id.id,
                  'state': 'draft',
                       }
                            #step2:debit side entry
            for rule in payslip.line_ids:
                if rule.amount !=0:
                    for cost_center in contract.cost_center_information_line:
                        account=self.env['account.account'].search([('salary_rule_id','=', rule.salary_rule_id.id),('controlled_id','=',cost_center.controlled_id.id),('company_id','=', payslip.employee_id.company_id.id)], limit=1)
                        if not account:
                            account=self.env['account.account'].search([('salary_rule_id','=', rule.salary_rule_id.id),('company_id','=', payslip.employee_id.company_id.id)], limit=1)
                        if account:
                            if rule.category_id.id in (4, 6):
                                credit_line = (0, 0, {
                                        'name': rule.name,
                                        'partner_id': payslip.employee_id.address_home_id.id,
                                        'debit': 0.0,
                                        'credit': abs((rule.amount/100)* cost_center.percentage_charged),
                                        'analytic_account_id': cost_center.cost_center.id,
                                        'account_id': account.id,
                                             })
                                line_ids.append(credit_line)
                                credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
                            elif rule.category_id.id !=5:
                                debit_line = (0, 0, {
                                        'name': rule.name,
                                        'partner_id': payslip.employee_id.address_home_id.id,
                                        'debit': abs((rule.amount/100)* cost_center.percentage_charged),
                                        'credit': 0.0,
                                        'analytic_account_id': cost_center.cost_center.id,
                                        'account_id': account.id,
                                             })
                                line_ids.append(debit_line)
                                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
                            #step3:credit side entry
                    if rule.category_id.id ==5:
                        credit_line = (0, 0, {
                                  'name': account.name,
                                  'partner_id': payslip.employee_id.address_home_id.id, 
                                  'debit': 0.0,
                                  'credit': abs(rule.amount), 
                                  'account_id': account.id,
                                          })
                        line_ids.append(credit_line)
                        credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
                            
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            payslip.update({
                'move_id': move.id,
            })

    
    
    
    
