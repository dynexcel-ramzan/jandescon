# -*- coding: utf-8 -*-

from odoo import models, fields, api, _



class HrExpense(models.Model):
    _inherit = 'hr.expense.sheet'
    

    def approve_expense_sheets(self):
        if not self.user_has_groups('hr_expense.group_hr_expense_team_approver'):
            pass
        elif not self.user_has_groups('hr_expense.group_hr_expense_manager'):
            current_managers = self.employee_id.expense_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot approve your own expenses"))

            if not self.env.user in current_managers and not self.user_has_groups('hr_expense.group_hr_expense_user') and self.employee_id.expense_manager_id != self.env.user:
                raise UserError(_("You can only approve your department expenses"))

        responsible_id = self.user_id.id or self.env.user.id    
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no expense reports to approve.'),
                'type': 'warning',
                'sticky': False,  #True/False will display for few seconds if false
            },
        }
        sheet_to_approve = self.filtered(lambda s: s.state in ['submit', 'draft'])
        if sheet_to_approve:
            notification['params'].update({
                'title': _('The expense reports were successfully approved.'),
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            })
            sheet_to_approve.write({'state': 'approve', 'user_id': responsible_id})
        self.activity_update()
        return notification
    
    
    def refuse_sheet(self, reason):
        if not self.user_has_groups('hr_expense.group_hr_expense_team_approver'):
            pass
        elif not self.user_has_groups('hr_expense.group_hr_expense_manager'):
            current_managers = self.employee_id.expense_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot refuse your own expenses"))

            if not self.env.user in current_managers and not self.user_has_groups('hr_expense.group_hr_expense_user') and self.employee_id.expense_manager_id != self.env.user:
                raise UserError(_("You can only refuse your department expenses"))

        self.write({'state': 'cancel'})
        for sheet in self:
            sheet.message_post_with_view('hr_expense.hr_expense_template_refuse_reason', values={'reason': reason, 'is_sheet': True, 'name': sheet.name})
        self.activity_update()







class HrExpense(models.Model):
    _inherit = 'hr.expense'
    
    @api.model
    def create(self,vals):
        if vals.get('code',_('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('hr.expense') or _('New')    
        res = super(HrExpense,self).create(vals)
        return res 
    
    code = fields.Char(
        'Reference', copy=False, readonly=True, default=lambda x: _('New'))
    category_id = fields.Many2one('approval.category', related='product_id.category_id', string="Category", required=False)
    approval_request_id = fields.Many2one('approval.request', string='Approval Request', copy=False, readonly=True)
    request_status = fields.Selection(related='approval_request_id.request_status')
    
    
    

    
    
    
    @api.model
    def create(self, vals):
        sheet = super(HrExpense, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)).create(vals)
        sheet.action_submit_expenses()
        sheet.action_submit()
        return sheet
    

    
    
    def action_submit(self):
        approver_ids  = []
        
        request_list = []
        for line in self:
            
            request_list.append({
                'name': line.employee_id.name + ' Has Expense Request on ' + str(line.date)+ ' For Amount ' + str(line.total_amount) + ' Sequence# ' +' ' + str(line.code) ,
                'request_owner_id': line.employee_id.user_id.id,
                'category_id': line.category_id.id,
                'expense_id': line.id,
                'reason': line.employee_id.name + ' Has Expense Request on ' + str(line.date)+ ' For Amount ' + str(line.total_amount) + ' Sequence# ' +' ' + str(line.code), 
                'request_status': 'new',
            })
            approval_request_id = self.env['approval.request'].create(request_list)
            approval_request_id._onchange_category_id()
            approval_request_id.action_confirm()
            line.approval_request_id = approval_request_id.id
