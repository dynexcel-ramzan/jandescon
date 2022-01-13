# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class HrEmployeeInherited(models.Model):
    _inherit = 'hr.employee'

    resource_calendar_ids = fields.Many2one('resource.calendar', 'Working Hours',)


class HrEmployeeShift(models.Model):
    _inherit = 'resource.calendar'

    def _get_default_attendance_ids(self):
        return [
            (0, 0, {'name': _('Monday Morning'), 'dayofweek': '0', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': _('Tuesday Morning'), 'dayofweek': '1', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': _('Wednesday Morning'), 'dayofweek': '2', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': _('Thursday Morning'), 'dayofweek': '3', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': _('Friday Morning'), 'dayofweek': '4', 'hour_from': 8, 'hour_to': 12}),
        ]

    color = fields.Integer(string='Color Index', help="Color")
    sequence = fields.Integer(string="Sequence", required=True, default=1, help="Sequence")
    attendance_ids = fields.One2many(
        'resource.calendar.attendance', 'calendar_id', 'Workingssss Time',
        copy=True, default=_get_default_attendance_ids)

    @api.depends('attendance_ids.hour_from', 'attendance_ids.hour_to')
    def _compute_hours_per_week(self):
        for calendar in self:
            if self.shift_type != 'night':
                sum_hours = sum((attendance.hour_to - attendance.hour_from) for attendance in calendar.attendance_ids)
                calendar.hours_per_week = sum_hours / 2 if calendar.two_weeks_calendar else sum_hours
                
            elif self.shift_type == 'night':
                sum_hours = sum(((24 - attendance.hour_from)  + attendance.hour_to) for attendance in calendar.attendance_ids)
                calendar.hours_per_week = sum_hours / 2 if calendar.two_weeks_calendar else sum_hours


