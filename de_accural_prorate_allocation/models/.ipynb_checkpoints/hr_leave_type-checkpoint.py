from odoo import fields, models, _, api


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    allocated_during_probation = fields.Boolean('Allocated during Probation')
