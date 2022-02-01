# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    ora_check_number = fields.Char(string='Check Number')
    ora_remarks = fields.Char(string='Remarks', compute='_compute_ora_remarks')
    
    def _compute_ora_remarks(self):
        for line in self:
            expense_sheet = self.env['hr.expense.sheet'].sudo().search([('employee_id.address_home_id','=',line.partner_id.id),('state','not in',('draft','cancel','done')),('total_amount','=',line.amount)])
            if expense_sheet and line.is_reconciled==False:
                line.update({
                    'ora_remarks': expense_sheet.name +' (Adjustment Forecast)',
                })
            else:
                line.update({
                    'ora_remarks': '',
                })    
        
    