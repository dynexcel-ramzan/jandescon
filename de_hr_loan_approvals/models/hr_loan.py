# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrLoan(models.Model):
    _inherit = 'hr.loan'
    
    
    category_id = fields.Many2one('approval.category', related='loan_type_id.category_id', string="Category", required=False)
    approval_request_id = fields.Many2one('approval.request', string='Approval Request', copy=False, readonly=True)
    request_status = fields.Selection(related='approval_request_id.request_status')
    
    
    @api.model
    def create(self, vals):
        sheet = super(HrLoan, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)).create(vals)
        sheet.action_submit()
        sheet.action_create_approval_request()
        
        return sheet
    
    
    def action_create_approval_request(self):
        approver_ids  = []
        
        
        
        request_list = []
        for line in self:
            request_list.append({
                'name': line.employee_id.name + ' Has Loan Request on ' + str(line.date)+ ' For Amount ' + str(line.loan_amount)+' '+' Sequence# '+str(line.name),
                'request_owner_id': line.employee_id.user_id.id,
                'category_id': line.category_id.id,
                'loan_id': line.id,
                'reason': ' Sequence# '+str(line.name)+ ' ' + line.employee_id.name + ' Has Loan Request on ' + str(line.date)+ ' For Amount ' + str(line.loan_amount),
                'request_status': 'new',
            })
            approval_request_id = self.env['approval.request'].create(request_list)
            approval_request_id._onchange_category_id()
            approval_request_id.action_confirm()
            line.approval_request_id = approval_request_id.id
