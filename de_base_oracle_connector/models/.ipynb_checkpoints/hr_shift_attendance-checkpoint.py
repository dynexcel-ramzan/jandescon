# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrShiftAttendance(models.Model):
    _name = 'hr.shift.attendance'
    _description = 'Employee Shift Attendance'
    _order = "check_in desc"
    
    def _default_employee(self):
        return self.env.user.employee_id
    

    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True, ondelete='cascade', index=True)
    date = fields.Date(string="Date", default=fields.date.today())
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
        readonly=True)
    shift_type = fields.Selection(selection=[
            ('morning', 'Morning'),
            ('posted', 'Evening'),
            ('night', 'Night')
        ], string='Status', copy=False, tracking=True,
        default='morning')
    shift_time_in = fields.Datetime(string="Shift Time In", default=fields.Datetime.now, required=True)
    shift_time_out = fields.Datetime(string="Shift Time Out")
    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=True)
    check_out = fields.Datetime(string="Check Out")
    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)
    overtime_hours = fields.Float(string='Overtime Hours', compute='_compute_overtime_hours', store=True, readonly=True)
    entry_type = fields.Char(string="Entry Type")
    
    
    
    @api.depends('check_in', 'check_out')
    def _compute_overtime_hours(self):
        for attendance in self:
            if attendance.check_out:
                delta = attendance.check_out - attendance.check_in
                if delta.total_seconds() > 28800:
                    overtime_delta = delta.total_seconds() - 28800
                    attendance.overtime_hours = overtime_delta / 3600.0
                else:
                    attendance.overtime_hours = False
            else:
                attendance.overtime_hours = False
                
    
    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out:
                delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = False

    

   
