# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    
    
    batch_type_id =  fields.Many2one('hr.payslip.run.type', string='Batch Type', required=True)
    category_id = fields.Many2one('approval.category', related='batch_type_id.category_id', string="Category", required=False)
    approval_request_id = fields.Many2one('approval.request', string='Approval Request', copy=False, readonly=True)
    request_status = fields.Selection(related='approval_request_id.request_status')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Verify'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('close', 'Done'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')
    
    
    
    @api.model
    def create(self, vals):
        sheet = super(HrPayslipRun, self).create(vals)
        if sheet.category_id:
            sheet.action_create_approval_request()        
        return sheet
    
    
    def action_create_approval_request(self):
        approver_ids  = []        
        request_list = []
        for line in self:
            request_list.append({
                'name': line.name + ' Batch Payslip Request Between ' + str(line.date_start)+ ' to ' + str(line.date_end),
                'request_owner_id': line.create_uid.id,
                'category_id': line.category_id.id,
                'batch_id': line.id,
                'reason': ' '+str(line.name)+ ' ' + str(line.create_uid.name) + ' Batch Payslip Request Between ' + str(line.date_start)+ ' to ' + str(line.date_end),
                'request_status': 'new',
            })
            approval_request_id = self.env['approval.request'].create(request_list)
            approval_request_id._onchange_category_id()
            approval_request_id.action_confirm()
            line.approval_request_id = approval_request_id.id

    
    
    def action_refuse(self):
        for batch in self:
            batch.update({
                'state': 'refused'
            })
            
            
    def action_approve(self):
        for batch in self:
            batch.update({
                'state': 'approved'
            })        
