# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
   
    
class ApprovalRequestInherit(models.Model):
    _inherit = 'approval.request'
    
    
    
    def action_confirm(self):
        if len(self.approver_ids) < self.approval_minimum:
            raise UserError(_("You have to add at least %s approvers to confirm your request.", self.approval_minimum))
        if self.requirer_document == 'required' and not self.attachment_number:
            raise UserError(_("You have to attach at lease one document."))
        approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new')
        
        approvers._create_activity()
        
        for approver in approvers:
            approver.write({'status': 'pending'})
            break
        self.write({'date_confirmed': fields.Datetime.now(), 'request_status':'pending'})
        
        
    def action_approve(self, approver=None):
        if not isinstance(approver, models.BaseModel):
            approver = self.mapped('approver_ids').filtered(
                lambda approver: approver.user_id == self.env.user
            )
        approver.write({'status': 'approved'})
        self.sudo()._get_user_approval_activities(user=self.env.user).action_feedback()
        approver_count = 0
        for approverid in self.approver_ids:
            if approverid.status == 'new':                
                approver_count = approver_count + 1
        if approver_count == 0:
            pass
        else:
            self.action_confirm()

    def action_refuse(self, approver=None):
        if not isinstance(approver, models.BaseModel):
            approver = self.mapped('approver_ids').filtered(
                lambda approver: approver.user_id == self.env.user
            )
        approver.write({'status': 'refused'})
        self.sudo()._get_user_approval_activities(user=self.env.user).action_feedback()    
        approver_count = 0
        for approverid in self.approver_ids:
            if approverid.status == 'new':
                
                approver_count = approver_count + 1
        if approver_count == 0:
            pass
        

        
        
    def recursive_manager(self, user):
        
        requested_employee = self.env['hr.employee'].search([('user_id','=',user)], limit=1)   
        requested_manager = self.env['hr.employee'].search([('id','=',requested_employee.parent_id.id)])
        return requested_manager.user_id.id
    

    
    
    @api.constrains('category_id')
    def _check_category(self):
        if self.category_id:
            if self.category_id.is_parent_approver == False:
                approver_data = []
                category = self.env['approval.category'].search([('id','=', self.category_id.id)])
                for approver in category.approval_category_line:
                    approver_data.append((0,0, {
                        'user_id': approver.user_id.id,
                    }))    
                self.approver_ids = approver_data
            else:
                approver_data = []
                approvers = []
                approval_level = self.category_id.approval_level
                approver = self.request_owner_id.id
                for level in range(approval_level, 0, -1):
                    approver = self.recursive_manager(approver)
                    if approver:
                        self.env['approval.approver'].create({
                            'request_id': self.id,
                            'user_id': approver,
                            'status' : 'new',  
                        })
                    

        
    

        
class ApprovalApproverInherit(models.Model):
    _inherit = 'approval.approver'
    
    department_id = fields.Many2one(related='user_id.department_id')
    job_title = fields.Char(related='user_id.job_title')
    sequence = fields.Integer(string='Sequence', default=10)



    

