# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

    

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    is_deposited = fields.Boolean(string='Deposit')
    
    def action_post(self):
        for line in self:
            if line.journal_id.name=='Blank Journal':
                raise UserError('Please Change Blank Journal!')
        res = super(AccountPayment, self).action_post()
        return res
    
    def action_payment_deposit(self):
        for line in self:
            if line.state == 'posted':
                line.update({
                    'is_deposited': True
                })
    
    
class HrEmployee(models.Model):
    _inherit = 'hr.employee'  
    
    
class ResUser(models.Model):
    _inherit = 'res.users'  
    
    
class ResPartner(models.Model):
    _inherit = 'res.partner'  
    