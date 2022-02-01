# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    # -------------------------------------------------------------------------
    # BUSINESS METHODS
    # -------------------------------------------------------------------------
    
    ora_check_number = fields.Char(string='Check Number')

    def _create_payments(self):
        # OVERRIDE to set the 'done' state on expense sheets.
        payments = super()._create_payments()
        expense_sheets = self.env['hr.expense.sheet'].search([('account_move_id', 'in', self.line_ids.move_id.ids)])
        for expense_sheet in expense_sheets:
            if expense_sheet.currency_id.is_zero(expense_sheet.amount_residual):
                expense_sheet.is_deposit_sign=True
                expense_sheet.state = 'done'
                
        return payments
    
    def _init_payments(self, to_process, edit_mode=False):
        # OVERRIDE
        payments = super()._init_payments(to_process, edit_mode=edit_mode)
        for payment, vals in zip(payments, to_process):
            expenses = vals['batch']['lines'].expense_id
            if expenses:
                payment.line_ids.write({'expense_id': expenses[0].id})
                payment.update({
                    'ora_check_number' : self.ora_check_number
                })
        return payments