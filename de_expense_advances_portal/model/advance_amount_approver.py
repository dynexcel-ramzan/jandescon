# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
    

class AdvanceAmountApprover(models.Model):
    _name = 'advance.amount.approver'  
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Advance Amount Approver'
    
    
    
    name = fields.Char(string="Name", required=True)
    date = fields.Date('Date', required=True)
    description = fields.Char('Description')
    company_id = fields.Many2one('res.company', string='Company', required=True)
    approver_line_ids=fields.One2many('advance.amount.approver.line', 'advance_id', string='Approver')
    
    @api.constrains('company_id')
    def _check_company(self):
        for expense in self:
            if expense.company_id:
                for line in expense.approver_line_ids:
                    line.update({
                        'company_id': line.company_id.id,
                    })    
    
    
    
class AdvanceAmountApprover(models.Model):
    _name = 'advance.amount.approver.line'  
    _description = 'Advance Amount Approver line'
    
    
    start_amount = fields.Float(string='Starting Amount', required=True, digits=(5,0))
    end_amount = fields.Float(string='Ending Amount', required=True, digits=(5,0))
    user_id = fields.Many2one('res.users', string='Approver', required=True)
    advance_id = fields.Many2one('advance.amount.approver', string='Approver Line')
    company_id = fields.Many2one('res.company', string='Company', required=True)
