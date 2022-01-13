# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrPayrollAccount(models.Model):
    _inherit = 'hr.payslip.run'
    
    
    
    def action_validate(self):
        """
            Generate the accounting entries related to the selected payslips
            A move is created for each journal and for each month.
        """
        res = super(HrPayrollAccount, self).action_validate()
        move = False
        for slip in self.slip_ids:
            move = slip.move_id
        if move != False:    
            new_move= move.copy()
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            new_move.line_ids.unlink() 
            for line in  move.line_ids:
                if line.debit > 0.0:
                    debit_line = (0, 0, {
                           'name': line.name,
                            'partner_id': line.partner_id.id,
                            'account_id': line.account_id.id,
                            'journal_id': line.journal_id.id,
                            'date': line.date,
                            'debit': line.credit,
                            'credit': line.debit,
                            'analytic_account_id': line.analytic_account_id.id,
                                     })
                    line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
                if line.credit > 0.0:
                    credit_line = (0, 0, {
                           'name': line.name,
                            'partner_id': line.partner_id.id,
                            'account_id': line.account_id.id,
                            'journal_id': line.journal_id.id,
                            'date': line.date,
                            'debit': line.credit,
                            'credit': line.debit,
                            'analytic_account_id': line.analytic_account_id.id,
                                     })
                    line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
                    #step3:credit side entry
            new_move['line_ids'] = line_ids  
        for line in self.slip_ids:
            line.update({
                'payslip_run_id': False,
                'move_id':  False,
            })
            line.action_payslip_done()
            for move_line in line.move_id.line_ids:
                move_line.update({
                    'partner_id':  line.employee_id.address_home_id.id if line.employee_id.address_home_id.id else False,
                })
            line.update({
                'payslip_run_id': self.id
            })    
                
 