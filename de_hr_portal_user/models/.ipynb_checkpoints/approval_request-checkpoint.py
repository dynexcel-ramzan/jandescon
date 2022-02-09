# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class ApprovalApprover(models.Model):
    _name = 'approval.approver'
    _description = 'Approver'

    _check_company_auto = True

    user_id = fields.Many2one('res.users', string="User", required=True, )
    employee_number = fields.Char(string='Employee Number', compute='_compute_employee_number')
    existing_request_user_ids = fields.Many2many('res.users', compute='_compute_existing_request_user_ids')
    status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], string="Status", default="new", readonly=True)
    request_id = fields.Many2one('approval.request', string="Request",
        ondelete='cascade', check_company=True)
    company_id = fields.Many2one(
        string='Company', related='request_id.company_id',
        store=True, readonly=True, index=True)
    
    @api.onchange('user_id')
    def _compute_employee_number(self):
        for line in self:
            line.update({
                'employee_number': self.env['hr.employee'].search([('user_id','=', line.user_id.id)], limit=1).emp_number,
            })

    def action_approve(self):
        self.request_id.action_approve(self)

    def action_refuse(self):
        self.request_id.action_refuse(self)

    def _create_activity(self):
        for approver in self:
            approver.request_id.activity_schedule(
                'approvals.mail_activity_data_approval',
                user_id=approver.user_id.id)

    @api.depends('request_id.request_owner_id', 'request_id.approver_ids.user_id')
    def _compute_existing_request_user_ids(self):
        for approver in self:
            approver.existing_request_user_ids = \
                self.mapped('request_id.approver_ids.user_id')._origin \
              | self.request_id.request_owner_id._origin


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    