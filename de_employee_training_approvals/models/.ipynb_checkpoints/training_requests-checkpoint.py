# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
from odoo.exceptions import UserError



class EmployeeRequest(models.Model):
    _inherit = 'employee.request'
    _description = 'Employee Requests Inh'
    
    
#     category_id = fields.Many2one(related='employee_id.resignation_category_id')
    category_id = fields.Many2one('approval.category')
    approval_request_id = fields.Many2one('approval.request', string="Approval")
    
            
    def action_refused(self):
        for line in self:
            line.update({
                'state': 'refused'
            })
            training_request_approval = self.env['approval.request'].search([('training_request_id','=', line.id)], limit=1)
            training_request_approval.action_cancel()
            
            
    @api.model
    def create(self, vals):
        default_app_category = self.env['approval.category'].search([('name','=','Training Request Approval')], order="id desc", limit=1)
#         raise UserError(default_app_category)
        vals['category_id'] = default_app_category.id
        
        sheet = super(EmployeeRequest, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)).create(vals)
        if sheet.category_id:
            sheet.action_create_approval_request_training()
        return sheet
    
    
    def action_create_approval_request_training(self):
        approver_ids  = []
        request_list = []

        for line in self:
            if line.category_id:
                employee_id = self.env['hr.employee'].search([('user_id','=',line.create_uid.id)], order="id desc", limit=1)
                
                request_list.append({
                        'name': str(employee_id.name) + ' Has Training Request of '+str(line.name),
                        'request_owner_id': line.create_uid.id,
                        'category_id': line.category_id.id,
                        'training_request_id': line.id,
                        'reason': line.reason,
                        'request_status': 'new',
                })
                approval_request_id = self.env['approval.request'].create(request_list)
                approval_request_id._onchange_category_id()
                approval_request_id.action_confirm()
                line.approval_request_id = approval_request_id.id
                