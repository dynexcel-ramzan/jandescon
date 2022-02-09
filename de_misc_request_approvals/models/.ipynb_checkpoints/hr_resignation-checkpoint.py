# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime




class HrResignation(models.Model):
    _inherit = 'hr.resignation'
    _description = 'Hr Resignation Inh'
    
    
#     user_id = fields.Many2one('res.users', string="User")
    category_id = fields.Many2one(related='employee_id.category_id')
    approval_request_id = fields.Many2one('approval.request', string="Approval")
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('submitted', 'To Approve'),
#         ('approved', 'Approved'),
#         ('refused', 'Refused')
#          ],
#         readonly=True, string='State', default='draft')
    
    
    def action_submit(self):
        for line in self:
            line.update({
                'state': 'submitted'
            })
            
    def action_approve(self):
        for line in self:
            line.update({
                'state': 'approved'
            }) 
            
                
            
    def action_refuse(self):
        for line in self:
            line.update({
                'state': 'refused'
            })
            resignation_approval = self.env['approval.request'].search([('resignation_id','=', line.id)], limit=1)
            resignation_approval.action_cancel()
            
            
            
            
            
    @api.model
    def create(self, vals):
        sheet = super(HrResignation, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)).create(vals)
        if sheet.category_id:
            sheet.action_create_approval_request_resignation()
        
        return sheet
    
    
    def action_create_approval_request_resignation(self):
        approver_ids  = []
        
        
        request_list = []
        for line in self:
            if line.category_id:
                request_list.append({
                        'name': line.employee_id.name + ' Has Resignation Request on  ',
                        'request_owner_id': line.employee_id.user_id.id,
                        'category_id': line.category_id.id,
                        'resignation_id': line.id,
                        'reason': line.employee_id.name + ' Has Attendance Rectification Request on ',
                        'request_status': 'new',
                })
                approval_request_id = self.env['approval.request'].create(request_list)
                approval_request_id._onchange_category_id()
                approval_request_id.action_confirm()
                line.approval_request_id = approval_request_id.id


    
    

    