# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HRLeaveType(models.Model):
    _inherit = 'hr.leave.type'
    
    leave_validation_type = fields.Selection(selection_add=[('approvals', 'By Multiple Approvals')])
    category_id = fields.Many2one('approval.category', string="Category", required=False)
    attachment = fields.Boolean(string="Attachment")
    attachment_validity = fields.Integer(string="Require after Days")
    is_ceo_approval = fields.Boolean(string="Approver")

