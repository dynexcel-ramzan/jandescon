import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class HrOvertimeWizard(models.TransientModel):
    _name = 'hr.overtime.wizard'
    _description = 'Hr Overtime Wizard'

    @api.model
    def _get_all_attendace_ids(self):
        all_ovt_attendance = self.env['hr.attendance'].search([('is_overtime', '=', False)])
        if all_ovt_attendance:
            return all_ovt_attendance.ids
        else:
            return []

    attendace_ids = fields.Many2many('hr.attendance', string='Attendace', default=_get_all_attendace_ids, domain=[('is_overtime', '=', False)])
    
    
    
    def cron_create_hr_overtime(self):
        attendance = self.env['hr.attendance']
        attendance.cron_create_overtime() 
    
    
    