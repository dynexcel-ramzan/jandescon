# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'
    
    expense_id = fields.Many2one('hr.expense.sheet', string='Expense Claim', required=False)
    
    def action_refuse(self, approver=None):
        res = super(ApprovalRequest, self).action_refuse()
        tot_approver_count = 0
        tot_refused_count = 0
        for approverid in self.approver_ids:                
            tot_approver_count = tot_approver_count + 1
        approver_count = 0
        for approverid in self.approver_ids:
            if  approverid.status == 'refused': 
                self.expense_id.sudo().refuse_sheet('Not Approved')
                
            if approverid.status == 'new':                
                approver_count = approver_count + 1
        if approver_count == 0:
            for approved in self.approver_ids:
                if  approved.status == 'refused': 
                    tot_refused_count = tot_refused_count + 1
                    self.expense_id.sudo().refuse_sheet('Not Approved')      
                    
            if tot_refused_count ==  tot_approver_count:
                if self.expense_id:
                    self.expense_id.sudo().refuse_sheet('Not Approved')         
      
        return res
    
    
    def action_approve(self, approver=None):      
        res = super(ApprovalRequest, self).action_approve()
        tot_approver_count = 0
        tot_approved_count = 0
        for approverid in self.approver_ids:                
            tot_approver_count = tot_approver_count + 1
        approver_count = 0
        for approverid in self.approver_ids:
            if approverid.status == 'new':                
                approver_count = approver_count + 1
        if approver_count == 0:
            for approved in self.approver_ids:
                if  approved.status == 'approved': 
                    tot_approved_count = tot_approved_count + 1
                    
            if tot_approver_count ==  tot_approved_count: 
                if self.expense_id:
                    self.expense_id.sudo().approve_expense_sheets()       
                        
        return res
    
    
    
    @api.depends('approver_ids.status')
    def _compute_request_status(self):
        for request in self:
            status_lst = request.mapped('approver_ids.status')
            minimal_approver = request.approval_minimum if len(status_lst) >= request.approval_minimum else len(status_lst)
            if status_lst:
                if status_lst.count('cancel'):
                    status = 'cancel'
                elif status_lst.count('refused'):
                    status = 'refused'
                elif status_lst.count('new'):
                    status = 'new'
                elif status_lst.count('approved') >= minimal_approver:
                    status = 'approved'
                    if request.expense_id:
                        request.expense_id.sudo().approve_expense_sheets()
                    
                elif status_lst.count('refused') >= minimal_approver:
                    status = 'refused'
                    if request.expense_id:
                        request.expense_id.sudo().action_refuse()    
                else:
                    status = 'pending'
            else:
                status = 'new'
            request.request_status = status
    
    
class ApprovalApprover(models.Model):
    _inherit = 'approval.approver'
    
    expense_id = fields.Many2one(related='request_id.expense_id')