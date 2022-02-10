# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
from odoo.exceptions import UserError, ValidationError



class AdvanceAgainstExpenses(models.Model):
    _inherit = 'advance.against.expense'
    _description = 'Advance Against Expenses Inh'
    
    
    categ_id = fields.Many2one('approval.category', string='Category')
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
        sheet.action_approval_category()
        sheet.action_amount_limitation()
        if sheet.categ_id:
            sheet.action_create_approval_request_adv_exp()
        return sheet
    
    
    def action_amount_limitation(self):
        for line in self:
            ext_approver_line = self.env['advance.amount.approver.line'].sudo().search([('end_amount','<', line.amount),('company_id','=', line.employee_id.company_id.id)], order='end_amount desc', limit=1)
            exceeding_limit = 0
            if ext_approver_line:
                exceeding_limit = ext_approver_line.end_amount
                raise UserError('You Are Not Allow to Enter Amount Greater than '+str(round(exceeding_limit))) 
    
    def action_approval_category(self):
        for line in self:
            expense_category=self.env['approval.category'].search([('name','=','Advance against Expense'),('company_id','=', line.employee_id.company_id.id)], limit=1)
            if not expense_category:
                category = {
                    'name': 'Advance against Expense',
                    'company_id': line.employee_id.company_id.id,
                    'is_parent_approver': True,
                }
                expense_category = self.env['approval.category'].sudo().create(category)
            line.categ_id=expense_category.id
            
    def action_create_approval_request_adv_exp(self):
        approver_ids  = []
        request_list = []
        for line in self:
            line.action_approval_category()
            request_list.append({
                    'name': str(line.employee_id.name)+ ' Advance Ref# '+str(line.name),
                    'request_owner_id': line.employee_id.user_id.id,
                    'category_id': line.categ_id.id,
                    'exp_adv_id': line.id,
                    'reason': 'Advance',
                    'request_status': 'new',
            })
            approval_request_id = self.env['approval.request'].sudo().create(request_list)
            approval_request_id._onchange_category_id()
            approval_request_id.action_confirm()
            line.approval_request_id = approval_request_id.id
            contract = self.env['hr.contract'].sudo().search([('employee_id','=', line.employee_id.id),('state','=', 'open')], limit=1)
            cost_center_approver = 0
            for cost_info in contract.cost_center_information_line:
                if cost_info.cost_center.approver_ids:
                    for cost_approver in cost_info.cost_center.approver_ids:
                        if cost_info.by_default==True:
                            already_approver = self.env['approval.approver'].search([('request_id','=',approval_request_id.id),('user_id','=', cost_approver.user_id.id)])
                            if not already_approver:
                                if cost_approver.user_id and not cost_approver.user_id.id==line.employee_id.parent_id.id:
                                    vals ={
                                            'user_id': cost_approver.user_id.id,
                                            'request_id': approval_request_id.id,
                                            'status': 'new',
                                    }
                                    approvers=self.env['approval.approver'].sudo().create(vals)
                                    cost_center_approver = cost_approver.user_id.id

            if line.employee_id.parent_id.id == line.employee_id.company_id.manager_id.id:
                pass
            elif line.employee_id.parent_id.id == line.employee_id.company_id.finance_partner_id.id:
                pass
            else:
                approver_line = self.env['advance.amount.approver.line'].sudo().search([('start_amount','<=', line.amount),('end_amount','>=', line.amount),('company_id','=', line.employee_id.company_id.id)], limit=1)
                if approver_line: 
                    if line.employee_id.parent_id.user_id.id == approver_line.user_id.id:
                        pass
                    elif cost_center_approver == approver_line.user_id.id:
                        pass
                    else:
                        vals ={
                                'user_id': approver_line.user_id.id,
                                'request_id': approval_request_id.id,
                                'status': 'new',
                        }
                        approvers=self.env['approval.approver'].sudo().create(vals)
                else:
                    ext_approver_line = self.env['advance.amount.approver.line'].sudo().search([('end_amount','<', line.amount),('company_id','=', line.employee_id.company_id.id)], order='end_amount desc', limit=1)
                    exceeding_limit = 0
                    if ext_approver_line:
                        exceeding_limit = ext_approver_line.end_amount
                    raise UserError('You Are Not Allow to Enter Amount Greater than '+str(round(exceeding_limit)))    
