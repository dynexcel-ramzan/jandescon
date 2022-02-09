# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'
    
    
    @api.model
    def create(self, vals):
        if vals.get('code',_('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('hr.expense.sheet') or _('New')  
        sheet = super(HrExpenseSheet, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)).create(vals)
        sheet.activity_update()
        return sheet
    
    
    
    
    
    def action_submit_sheet(self):
        sheet = super(HrExpenseSheet, self).action_submit_sheet()
        self.action_submit()
        return sheet
    
    code = fields.Char(
        'Reference', copy=False, readonly=True, default=lambda x: _('New'))
    category_id = fields.Many2one('approval.category', string="Category", required=False)
    approval_request_id = fields.Many2one('approval.request', string='Approval Request', copy=False, readonly=True)
    request_status = fields.Selection(related='approval_request_id.request_status')
    
    def action_approval_category(self):
        for line in self:
            expense_category=self.env['approval.category'].search([('name','=','Expense Claim'),('company_id','=', line.company_id.id)], limit=1)
            if not expense_category:
                category = {
                    'name': 'Expense Claim',
                    'company_id': line.employee_id.company_id.id,
                    'is_parent_approver': False,
                }
                expense_category = self.env['approval.category'].sudo().create(category)
            line.category_id=expense_category.id
    
    
    def action_submit(self):
        approver_ids  = []
        request_list = []
        for line in self:
            is_managerial_approvals = False
            for expense_line in line.expense_sheet_line_ids:
                if expense_line.sub_category_id.management_approval==True:
                    is_managerial_approvals = True
            # Exception Approvals        
            if line.exception==True:
                line.action_approval_category()
                request_list.append({
                    'name': line.employee_id.name ,
                    'request_owner_id': line.employee_id.user_id.id,
                    'category_id': line.category_id.id,
                    'expense_id': line.id,
                    'reason': str(line.ora_category_id.name) +' ('+'Exception'+')', 
                    'request_status': 'new',
                })
                approval_request_id = self.env['approval.request'].sudo().create(request_list)
                if line.employee_id.parent_id.user_id.id:
                    vals ={
                        'user_id': line.employee_id.parent_id.user_id.id,
                        'request_id': approval_request_id.id,
                        'status': 'new',
                    }
                    approvers=self.env['approval.approver'].sudo().create(vals)
                if line.employee_id.company_id.hr_id.user_id and line.employee_id.company_id.hr_id.user_id.id !=line.employee_id.parent_id.user_id.id :
                    vals ={
                        'user_id': line.employee_id.company_id.hr_id.user_id.id,
                        'request_id': approval_request_id.id,
                        'status': 'new',
                    }
                    approvers=self.env['approval.approver'].sudo().create(vals)
                if line.employee_id.company_id.finance_partner_id.user_id and  line.employee_id.company_id.finance_partner_id.user_id.id not in (line.employee_id.company_id.hr_id.user_id.id, line.employee_id.parent_id.user_id.id):    
                    vals ={
                        'user_id': line.employee_id.company_id.finance_partner_id.user_id.id,
                        'request_id': approval_request_id.id,
                        'status': 'new',
                    }
                    approvers=self.env['approval.approver'].sudo().create(vals)    
                if line.employee_id.company_id.manager_id.user_id and  line.employee_id.company_id.manager_id.user_id.id not in (line.employee_id.parent_id.user_id.id, line.employee_id.company_id.finance_partner_id.user_id.id,line.employee_id.company_id.hr_id.user_id.id):
                    vals ={
                        'user_id': line.employee_id.company_id.manager_id.user_id.id,
                        'request_id': approval_request_id.id,
                        'status': 'new',
                    }
                    approvers=self.env['approval.approver'].sudo().create(vals)         
                approval_request_id._onchange_category_id()
                approval_request_id.action_confirm()
                line.approval_request_id = approval_request_id.id
                
            # Finance Bussiness Approvals       
            elif line.employee_id.company_id.is_fbp_approval==True:
                line.action_approval_category()
                request_list.append({
                    'name': line.employee_id.name ,
                    'request_owner_id': line.employee_id.user_id.id,
                    'category_id': line.category_id.id,
                    'expense_id': line.id,
                    'reason': str(line.ora_category_id.name), 
                    'request_status': 'new',
                })
                approval_request_id = self.env['approval.request'].sudo().create(request_list)
                if line.employee_id.company_id.finance_partner_id.user_id :
                    vals ={
                        'user_id': line.employee_id.company_id.finance_partner_id.user_id.id,
                        'request_id': approval_request_id.id,
                        'status': 'new',
                    }
                    approvers=self.env['approval.approver'].sudo().create(vals)
                    approval_request_id._onchange_category_id()
                    approval_request_id.action_confirm()
                    line.approval_request_id = approval_request_id.id
                if line.ora_category_id.is_manager==True:     
                    if line.employee_id.parent_id.user_id and line.employee_id.company_id.finance_partner_id.user_id.id != line.employee_id.parent_id.user_id.id:
                        vals ={
                            'user_id': line.employee_id.parent_id.user_id.id,
                            'request_id': approval_request_id.id,
                            'status': 'pending',
                        }
                        approvers=self.env['approval.approver'].sudo().create(vals)
                 
                # Extra Approvals 
                if  line.ora_category_id.hr_approval==True and is_managerial_approvals==True:
                    if line.ora_category_id.is_manager==False:
                        if line.employee_id.company_id.hr_id and line.employee_id.company_id.hr_id.user_id.id !=  line.employee_id.company_id.finance_partner_id.user_id.id:
                            vals ={
                                'user_id': line.employee_id.company_id.hr_id.user_id.id,
                                'request_id': approval_request_id.id,
                                'status': 'pending',
                            }
                            approvers=self.env['approval.approver'].sudo().create(vals)
                        if line.employee_id.company_id.manager_id and line.employee_id.company_id.manager_id.id not in  (line.employee_id.company_id.finance_partner_id.user_id.id, line.employee_id.company_id.hr_id.user_id.id):
                            vals ={
                                'user_id': line.employee_id.company_id.manager_id.user_id.id,
                                'request_id': approval_request_id.id,
                                'status': 'pending',
                            }
                            approvers=self.env['approval.approver'].sudo().create(vals)  
                    else:
                        if line.employee_id.company_id.hr_id and line.employee_id.company_id.hr_id.user_id.id !=  line.employee_id.company_id.finance_partner_id.user_id.id:
                            vals ={
                                'user_id': line.employee_id.company_id.hr_id.user_id.id,
                                'request_id': approval_request_id.id,
                                'status': 'pending',
                            }
                            approvers=self.env['approval.approver'].sudo().create(vals)
                        if line.employee_id.company_id.manager_id and line.employee_id.company_id.hr_id.user_id.id not in  (line.employee_id.company_id.finance_partner_id.user_id.id, line.employee_id.company_id.hr_id.user_id.id):
                            vals ={
                                'user_id': line.employee_id.company_id.manager_id.user_id.id,
                                'request_id': approval_request_id.id,
                                'status': 'pending',
                            }
                            approvers=self.env['approval.approver'].sudo().create(vals)
                elif  line.ora_category_id.hr_approval==True:
                    if line.ora_category_id.is_manager==False:
                        if line.employee_id.company_id.hr_id and line.employee_id.company_id.hr_id.user_id.id !=  line.employee_id.company_id.finance_partner_id.user_id.id:
                            vals ={
                                'user_id': line.employee_id.company_id.hr_id.user_id.id,
                                'request_id': approval_request_id.id,
                                'status': 'pending',
                            }
                            approvers=self.env['approval.approver'].sudo().create(vals)
                    else:
                        if line.employee_id.company_id.hr_id and line.employee_id.company_id.hr_id.user_id.id not in  (line.employee_id.company_id.finance_partner_id.user_id.id, line.employee_id.parent_id.user_id.id):
                            vals ={
                                'user_id': line.employee_id.company_id.hr_id.user_id.id,
                                'request_id': approval_request_id.id,
                                'status': 'pending',
                            }
                            approvers=self.env['approval.approver'].sudo().create(vals)
                elif is_managerial_approvals==True:
                    if line.ora_category_id.is_manager==False:
                        if line.employee_id.company_id.manager_id and line.employee_id.company_id.manager_id.user_id.id !=  line.employee_id.company_id.finance_partner_id.user_id.id:
                            vals ={
                                'user_id': line.employee_id.company_id.manager_id.user_id.id,
                                'request_id': approval_request_id.id,
                                'status': 'pending',
                            }
                            approvers=self.env['approval.approver'].sudo().create(vals)
                    else:
                        if line.employee_id.company_id.manager_id and line.employee_id.company_id.manager_id.user_id.id not in  (line.employee_id.company_id.finance_partner_id.user_id.id, line.employee_id.parent_id.user_id.id):
                            vals ={
                                'user_id': line.employee_id.company_id.manager_id.user_id.id,
                                'request_id': approval_request_id.id,
                                'status': 'pending',
                            }
                            approvers=self.env['approval.approver'].sudo().create(vals)            
                        
            # Normal Flow Approvals 
            else:
                if line.ora_category_id.is_manager==True:
                    line.action_approval_category()
                    request_list.append({
                        'name': line.employee_id.name ,
                        'request_owner_id': line.employee_id.user_id.id,
                        'category_id': line.category_id.id,
                        'expense_id': line.id,
                        'reason': str(line.ora_category_id.name),
                        'request_status': 'new',
                    })
                    approval_request_id = self.env['approval.request'].sudo().create(request_list)
                    if line.employee_id.parent_id.user_id :
                        vals ={
                            'user_id': line.employee_id.parent_id.user_id.id,
                            'request_id': approval_request_id.id,
                            'status': 'pending',
                        }
                        approvers=self.env['approval.approver'].sudo().create(vals)
                        
                    approval_request_id._onchange_category_id()
                    approval_request_id.action_confirm()
                    line.approval_request_id = approval_request_id.id
                    # Extra Approvals 
                    if  line.ora_category_id.hr_approval==True and is_managerial_approvals==True:
                        if line.employee_id.company_id.hr_id and line.employee_id.company_id.hr_id.user_id.id !=  line.employee_id.parent_id.user_id.id:
                            vals ={
                                'user_id': line.employee_id.company_id.hr_id.user_id.id,
                                'request_id': approval_request_id.id,
                                'status': 'pending',
                            }
                            approvers=self.env['approval.approver'].sudo().create(vals)
                        if line.employee_id.company_id.manager_id and line.employee_id.company_id.manager_id.id not in  (line.employee_id.parent_id.user_id.id, line.employee_id.company_id.hr_id.user_id.id):
                            vals ={
                                'user_id': line.employee_id.company_id.manager_id.user_id.id,
                                'request_id': approval_request_id.id,
                                'status': 'pending',
                            }
                            approvers=self.env['approval.approver'].sudo().create(vals)  
                else:
                    if  line.ora_category_id.hr_approval==True and is_managerial_approvals==True:
                        line.action_approval_category()
                        request_list.append({
                            'name': line.employee_id.name ,
                            'request_owner_id': line.employee_id.user_id.id,
                            'category_id': line.category_id.id,
                            'expense_id': line.id,
                            'reason': str(line.ora_category_id.name),
                            'request_status': 'new',
                        })
                        approval_request_id = self.env['approval.request'].sudo().create(request_list)
                        # Extra Approvals 
                        if line.employee_id.company_id.hr_id and line.employee_id.company_id.hr_id.user_id.id !=  line.employee_id.parent_id.user_id.id:
                            vals ={
                                'user_id': line.employee_id.company_id.hr_id.user_id.id,
                                'request_id': approval_request_id.id,
                                'status': 'pending',
                            }
                            approvers=self.env['approval.approver'].sudo().create(vals)
                        if line.employee_id.company_id.manager_id and line.employee_id.company_id.manager_id.id not in  (line.employee_id.parent_id.user_id.id, line.employee_id.company_id.hr_id.user_id.id):
                            vals ={
                                'user_id': line.employee_id.company_id.manager_id.user_id.id,
                                'request_id': approval_request_id.id,
                                'status': 'pending',
                            }
                            approvers=self.env['approval.approver'].sudo().create(vals)
                        approval_request_id._onchange_category_id()
                        approval_request_id.action_confirm()
                        line.approval_request_id = approval_request_id.id
                    elif line.ora_category_id.hr_approval==True:
                        line.action_approval_category()
                        request_list.append({
                            'name': line.employee_id.name ,
                            'request_owner_id': line.employee_id.user_id.id,
                            'category_id': line.category_id.id,
                            'expense_id': line.id,
                            'reason': str(line.ora_category_id.name),
                            'request_status': 'new',
                        })
                        approval_request_id = self.env['approval.request'].sudo().create(request_list)
                        # Extra Approvals 
                        if line.employee_id.company_id.hr_id :
                            vals ={
                                'user_id': line.employee_id.company_id.hr_id.user_id.id,
                                'request_id': approval_request_id.id,
                                'status': 'pending',
                            }
                            approvers=self.env['approval.approver'].sudo().create(vals)
                            approval_request_id._onchange_category_id()
                            approval_request_id.action_confirm()
                            line.approval_request_id = approval_request_id.id
                        
                    elif is_managerial_approvals==True:
                        line.action_approval_category()
                        request_list.append({
                            'name': line.employee_id.name ,
                            'request_owner_id': line.employee_id.user_id.id,
                            'category_id': line.category_id.id,
                            'expense_id': line.id,
                            'reason': str(line.ora_category_id.name),
                            'request_status': 'new',
                        })
                        approval_request_id = self.env['approval.request'].sudo().create(request_list)
                        # Extra Approvals 
                        if line.employee_id.company_id.manager_id:
                            vals ={
                                'user_id': line.employee_id.company_id.manager_id.user_id.id,
                                'request_id': approval_request_id.id,
                                'status': 'pending',
                            }
                            approvers=self.env['approval.approver'].sudo().create(vals)
                            approval_request_id._onchange_category_id()
                            approval_request_id.action_confirm()
                            line.approval_request_id = approval_request_id.id    
                        
            # Vehicle Meter Approvals         
            if line.ora_category_id.vehicle_meter_approval==True:
                if line.employee_id.work_location_id.approver_id :
                    if line.employee_id.work_location_id.approver_id.user_id:
                        if not line.approval_request_id:
                            line.action_approval_category()
                            request_list.append({
                                'name': line.employee_id.name ,
                                'request_owner_id': line.employee_id.user_id.id,
                                'category_id': line.category_id.id,
                                'expense_id': line.id,
                                'reason': str(line.ora_category_id.name),
                                'request_status': 'new',
                            })
                            approval_request_id = self.env['approval.request'].sudo().create(request_list)
                            
                            vals ={
                              'user_id': line.employee_id.work_location_id.approver_id.user_id.id,
                              'request_id': approval_request_id.id,
                              'status': 'pending',
                            }
                            approvers=self.env['approval.approver'].sudo().create(vals)
                            approval_request_id._onchange_category_id()
                            approval_request_id.action_confirm()
                            line.approval_request_id = approval_request_id.id
                        else:    
                            approver_list = []
                            for approver_line in line.approval_request_id.approver_ids:
                                approver_list.append(approver_line.user_id.id)
                            line.approval_request_id.update({
                                'request_status': 'new',
                            })    
                            line.approval_request_id.approver_ids.unlink()    
                            vals ={
                                'user_id': line.employee_id.work_location_id.approver_id.user_id.id,
                                'request_id': line.approval_request_id.id,
                                'status': 'pending',
                            }
                            approvers=self.env['approval.approver'].sudo().create(vals)
                            for approver in approver_list:
                                vals ={
                                'user_id': approver,
                                'request_id': line.approval_request_id.id,
                                'status': 'new',
                                }
                                approvers=self.env['approval.approver'].sudo().create(vals)

                
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
    
    
    
    

    
    
    
