# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime


class AdvanceAgainstExpenses(models.Model):
    _inherit = 'advance.against.expense'
    _description = 'Advance Against Expenses Inh'
    
    
    category_id = fields.Many2one('approval.category', related='employee_id.adv_exp_id')
    approval_request_id = fields.Many2one('approval.request', string="Approval")
    
            
    def action_reject(self):
        for line in self:
            line.update({
                'state': 'reject'
            })
            adv_exp_approval = self.env['approval.request'].search([('exp_adv_id','=', line.id)], limit=1)
            adv_exp_approval.action_cancel()
            
            
    @api.model
    def create(self, vals):
        sheet = super(AdvanceAgainstExpenses, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)).create(vals)
        if sheet.category_id:
            sheet.action_create_approval_request_adv_exp()
        return sheet
    
    def action_approval_category(self):
        for line in self:
            expense_category=self.env['approval.category'].search([('name','=','Expense Advances'),('company_id','=', line.employee_id.company_id.id)], limit=1)
            if not expense_category:
                category = {
                    'name': 'Expense Claim',
                    'company_id': line.employee_id.company_id.id,
                    'is_parent_approver': True,
                }
                expense_category = self.env['approval.category'].sudo().create(category)
            line.category_id=expense_category.id
            
    def action_create_approval_request_adv_exp(self):
        approver_ids  = []
        request_list = []
        for line in self:
            line.action_approval_category()
            request_list.append({
                    'name': str(line.employee_id.name)+ ' Expense Request Ref# '+str(line.name)+' Amount: '+str(line.amount),
                    'request_owner_id': line.employee_id.user_id.id,
                    'category_id': line.category_id.id,
                    'exp_adv_id': line.id,
                    'reason': 'Expense Advances',
                    'request_status': 'new',
            })
            approval_request_id = self.env['approval.request'].sudo().create(request_list)
            approval_request_id._onchange_category_id()
            approval_request_id.action_confirm()
            line.approval_request_id = approval_request_id.id
            contract = self.env['hr.contract'].sudo().search([('employee_id','=', line.employee_id.id),('state','=', 'open')], limit=1)
            for cost_info in contract.cost_center_information_line:
                if cost_info.cost_center.approver_ids:
                    for cost_approver in cost_info.cost_center.approver_ids:
                        already_approver = self.env['approval.approver'].search([('request_id','=',approval_request_id.id),('user_id','=', cost_approver.user_id.id)])
                        if not already_approver:
                            if cost_approver.user_id and not cost_approver.user_id.id==line.employee_id.parent_id.id:
                                vals ={
                                        'user_id': cost_approver.user_id.id,
                                        'request_id': approval_request_id.id,
                                        'status': 'new',
                                }
                                approvers=self.env['approval.approver'].sudo().create(vals)

            if line.employee_id.parent_id.id == line.employee_id.company_id.manager_id.id:
                pass
            elif line.employee_id.parent_id.id == line.employee_id.company_id.finance_partner_id.id:
                pass
            else:
                approver_line = self.env['advance.amount.approver.line'].sudo().search([('start_amount','<=', line.amount),('end_amount','>=', line.amount),('company_id','=', line.employee_id.company_id.id)], limit=1)
                if approver_line: 
                    if line.employee_id.parent_id.user_id.id == approver_line.user_id.id:
                        pass
                    else:
                        vals ={
                                'user_id': approver_line.user_id.id,
                                'request_id': approval_request_id.id,
                                'status': 'new',
                        }
                        approvers=self.env['approval.approver'].sudo().create(vals)
                else:
                    ext_approver_line = self.env['advance.amount.approver.line'].sudo().search([('end_amount','<=', line.amount),('company_id','=', line.employee_id.company_id.id)], limit=1)

                    if ext_approver_line:
                        if line.employee_id.parent_id.user_id.id == ext_approver_line.user_id.id:
                            pass
                        else:
                            vals ={
                                    'user_id': ext_approver_line.user_id.id,
                                    'request_id': approval_request_id.id,
                                    'status': 'new',
                            }
                            approvers=self.env['approval.approver'].sudo().create(vals)    
