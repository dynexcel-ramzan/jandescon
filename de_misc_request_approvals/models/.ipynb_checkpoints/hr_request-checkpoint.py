# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime




class HrRequest(models.Model):
    _inherit = 'hr.request'
    _description = 'Hr Request Inh'
    
    
    category_id = fields.Many2one(related='request_type_id.approval_category_id')
    approval_request_id = fields.Many2one('approval.request', string="Approval")
            
    def action_refused(self):
        for line in self:
            line.update({
                'state': 'refused'
            })
            resignation_approval = self.env['approval.request'].search([('misc_request_id','=', line.id)], limit=1)
            resignation_approval.action_cancel()
            
            
    @api.model
    def create(self, vals):
        sheet = super(HrRequest, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)).create(vals)
        if sheet.category_id:
            sheet.action_create_misc_request_approval_request()
        return sheet
    
    
    def action_create_misc_request_approval_request(self):
        approver_ids  = []
        request_list = []

        for line in self:
            if line.category_id:
                request_list.append({
                        'name': line.employee_id.name + ' Has Misc Request against ref #'+str(line.name),
                        'request_owner_id': line.employee_id.user_id.id,
                        'category_id': line.category_id.id,
                        'misc_request_id': line.id,
                        'reason': line.employee_id.name + ' Has Misc Request against ref #'+str(line.name),
                        'request_status': 'new',
                })
                approval_request_id = self.env['approval.request'].create(request_list)
                approval_request_id._onchange_category_id()
                approval_request_id.action_confirm()
                line.approval_request_id = approval_request_id.id


    
    

    