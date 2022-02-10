# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
    

class AdvanceAgainstExpense(models.Model):
    _name = 'advance.against.expense'  
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Advance Against Expense'
    
    @api.model
    def create(self, values):
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code('advance.against.expense.sequence') or _('New')
        return super(AdvanceAgainstExpense, self).create(values)
    
    
    def unlink(self):
        raise UserError(('Deletion is not allowed!'))
    
    def send_for_approval(self):
        self.state = 'waiting'
        
    def action_reject(self):
        self.state = 'reject'
        
    def action_approve(self):
        vals = {
            'partner_id': self.partner_id.id,            
            'date': self.date,
            'journal_id': self.env['account.journal'].search([('company_id','=',self.employee_id.company_id.id),('name','=','Blank Journal')], limit=1).id,
            'amount': self.amount,
            'ref': self.description,
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            }
        record = self.env['account.payment'].sudo().create(vals)
        self.payment_entry_ref = record.id
        self.state = 'approved'
        record.move_id.update({
            'expense_advance_id': self.id,
        })
    
    
    name = fields.Char(string="Name", required=True, copy=False, readonly=True, index=True,
                          default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', related='employee_id.user_id.partner_id', string='Partner')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    amount = fields.Float('Amount')
    date = fields.Date('Date')
    description = fields.Char('Description')
    state = fields.Selection([('draft','Draft'), ('waiting','Waiting Approval'), ('approved','Approved'), ('reject','Reject')], string='State', default='draft')
    payment_entry_ref = fields.Many2one('account.payment')
    
    
    
