# -*- coding: utf-8 -*-
from odoo.exceptions import Warning
from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime




class HrEmployee(models.Model):
    _inherit = 'hr.attendance'

    
    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = False
    
    @api.depends('check_in', 'check_out','employee_id')
    def _inverse_shift(self):
        for attendance in self:
            attendance.update({
                'shift_id': attendance.shift_id
            })
    
    

   
    
    
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime


class HrAttendance(models.Model):
    _inherit = "hr.attendance"
    _description = "Attendance"
    _order = "check_in desc"

    shift_id = fields.Many2one('resource.calendar', string="Shift", help="Shift schedule", compute='_compute_employee_shift_attendance')
    shift_type_id = fields.Many2one('resource.calendar', string="Shift")

    @api.depends('check_in', 'check_out','employee_id')
    def _compute_employee_shift_attendance(self):
        for attendance in self:
            shift_general = self.env['resource.calendar'].search([], limit=1)
            attendance.shift_id = shift_general.id
            attendance.shift_type_id = shift_general.id
            shift_one = self.env['resource.calendar'].search([('company_id','=',attendance.employee_id.company_id.id)], limit=1)
            attendance.shift_id = shift_one.id
            attendance.shift_type_id = shift_one.id
            attendee_date = fields.date.today().strftime('%Y-%m-%d') 
            if attendance.check_in:
                attendee_date = attendance.check_in.strftime('%Y-%m-%d')
            elif attendance.check_out:
                attendee_date = attendance.check_out.strftime('%Y-%m-%d')
            shift_contract = self.env['hr.shift.schedule.line'].search([('employee_id','=', attendance.employee_id.id),('date','=',attendee_date),('state','=','posted')], limit=1)
            if shift_contract.first_shift_id and shift_contract.second_shift_id:
                shift_one1 = 0
                shift_two1 = 0
                date_hour1 = datetime.strptime(attendee_date, '%Y-%m-%d') + relativedelta(hours =+ 0) 
                for attendee in shift_contract.first_shift_id.attendance_ids:
                    week_day = shift_contract.day.id - 1
                    if str(week_day) == attendee.dayofweek:
                        date_from = date_hour1 + relativedelta(hours =+ attendee.hour_from) - relativedelta(hours =+ 7)
                        date_to = date_hour1 + relativedelta(hours =+ attendee.hour_to) - relativedelta(hours =+ 5)
                        if str(attendance.check_in) >= str(date_from) and str(attendance.check_in) <= str(date_to):
                            shift_one1 = shift_contract.first_shift_id.id   
                            
                            
                for attendee in shift_contract.second_shift_id.attendance_ids:
                    week_day = shift_contract.day.id - 1
                    if str(week_day) == attendee.dayofweek:
                        date_from = date_hour1 + relativedelta(hours =+ attendee.hour_from) - relativedelta(hours =+ 7)
                        date_to = date_hour1 + relativedelta(hours =+ attendee.hour_to) - relativedelta(hours =+ 5)
                        
                        if str(attendance.check_in) >= str(date_from):
                            shift_two1 = shift_contract.second_shift_id.id   
                               
                            
                                                         
                        
                if shift_one1 > 0:
                    attendance.shift_id = shift_one1
                    attendance.shift_type_id = shift_one1
                    employee_active_shift = self.env['hr.employee'].search([('id','=', attendance.employee_id.id)])
                    employee_active_shift.update({
                           'shift_id': shift_one1
                        })
                    
                if shift_two1 > 0:           
                    attendance.shift_id = shift_two1
                    attendance.shift_type_id = shift_two1
                    employee_active_shift = self.env['hr.employee'].search([('id','=', attendance.employee_id.id)])
                    employee_active_shift.update({
                           'shift_id': shift_two1
                        })    

            elif shift_contract.first_shift_id:
                shift_one =  shift_contract.first_shift_id 
                attendance.shift_id = shift_one.id
                attendance.shift_type_id = shift_one.id
                employee_active_shift = self.env['hr.employee'].search([('id','=', attendance.employee_id.id)])
                employee_active_shift.update({
                    'shift_id': shift_one.id
                        })
            
            
            elif shift_contract.second_shift_id:
                shift_two =  shift_contract.second_shift_id           
                attendance.shift_id = shift_two.id
                attendance.shift_type_id = shift_two.id
                employee_active_shift = self.env['hr.employee'].search([('id','=', attendance.employee_id.id)])
                employee_active_shift.update({
                    'shift_id': shift_two.id
                        }) 
                
     


    def _default_employee(self):
        return self.env.user.employee_id

    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True, ondelete='cascade', index=True)
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
        readonly=True)
    check_in = fields.Datetime(string="Check In")
    check_out = fields.Datetime(string="Check Out")
    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)

    def name_get(self):
        result = []
        for attendance in self:
            if not attendance.check_out:
                result.append((attendance.id, _("%(empl_name)s from %(check_in)s") % {
                    'empl_name': attendance.employee_id.name,
                    'check_in': format_datetime(self.env, attendance.check_in, dt_format=False),
                }))
            else:
                result.append((attendance.id, _("%(empl_name)s from %(check_in)s to %(check_out)s") % {
                    'empl_name': attendance.employee_id.name,
                    'check_in': format_datetime(self.env, attendance.check_in, dt_format=False),
                    'check_out': format_datetime(self.env, attendance.check_out, dt_format=False),
                }))
        return result

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = False

    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                if attendance.check_out < attendance.check_in:
                    raise exceptions.ValidationError(_('"Check Out" time cannot be earlier than "Check In" time.'))

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
                raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                    'empl_name': attendance.employee_id.name,
                    'datetime': format_datetime(self.env, attendance.check_in, dt_format=False),
                })

            if not attendance.check_out:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if no_check_out_attendances:
                    raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
                        'empl_name': attendance.employee_id.name,
                        'datetime': format_datetime(self.env, no_check_out_attendances.check_in, dt_format=False),
                    })
            else:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_in', '<', attendance.check_out),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
                    raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                        'empl_name': attendance.employee_id.name,
                        'datetime': format_datetime(self.env, last_attendance_before_check_out.check_in, dt_format=False),
                    })

    @api.returns('self', lambda value: value.id)
    def copy(self):
        raise exceptions.UserError(_('You cannot duplicate an attendance.'))
    


    