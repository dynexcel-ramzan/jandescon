# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    
    att_date = fields.Date(string="Attendance Date")
    oralce_employee_no = fields.Char(related='employee_id.emp_number')
    work_location_id = fields.Many2one('hr.work.location', string='Work Location')

    def action_update_out_time(self):
        for attendance in self:
            if attendance.check_out == False:
                hour_from = 4
                hour_to =  12
                attendance_date = attendance.att_date
                for  shift_line in attendance.shift_id.attendance_ids:
                    hour_from = shift_line.hour_from
                    hour_to = shift_line.hour_to
                    if attendance_date.weekday() == shift_line.dayofweek:
                      hour_from = shift_line.hour_from
                      hour_to = shift_line.hour_to    
                date_hour_from = attendance_date + relativedelta(hours =+ hour_from)
                date_hour_to =  attendance_date + relativedelta(hours =+ hour_to) 
                check_in = attendance.check_in + relativedelta(hours =+ 5) 
                if check_in >= date_hour_from and check_in <= date_hour_to:
                    delta = date_hour_to - check_in
                    deltain = delta.total_seconds()
                    if deltain <= 7200:
                        attendance.update( {
                                    'check_in': False,
                                    'check_out': attendance.check_in
                                    })
                elif check_in >= date_hour_to:
                    attendance.update( {
                                  'check_in': False,
                                  'check_out': attendance.check_in
                                  })   


    def action_process_attendance(self, attendance_id):
        hr_attendances = self.env['hr.attendance'].search([('id','=', attendance_id)])
        for attendance in hr_attendances:
            if not attendance.check_out and attendance.check_in:
                if attendance.shift_id:
                    hour_from = 4
                    attendance_date1 = attendance.check_in.strftime("%Y-%m-%d")
                    hour_to =  12
                    attendance_date = datetime.strptime(str(attendance_date1), '%Y-%m-%d')
                    for  shift_line in attendance.shift_id.attendance_ids:
                        hour_from = shift_line.hour_from
                        hour_to = shift_line.hour_to
                        if attendance_date.weekday() == shift_line.dayofweek:
                            hour_from = shift_line.hour_from
                            hour_to = shift_line.hour_to    
                    date_hour_from = attendance_date + relativedelta(hours =+ hour_from)
                    date_hour_to =  attendance_date + relativedelta(hours =+ hour_to) 
                    check_in = attendance.check_in + relativedelta(hours =+ 5) 
                    if check_in >= date_hour_from and check_in <= date_hour_to:
                        delta = date_hour_to - check_in
                        deltain = delta.total_seconds()
                        if deltain <= 7200:
                            attendance.update( {
                                    'check_in': False,
                                    'check_out': attendance.check_in
                                })
                    elif check_in >= date_hour_to:
                        attendance.update( {
                                  'check_in': False,
                                  'check_out': attendance.check_in
                        })
                        
    
    
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
           
            if not attendance.check_out:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if no_check_out_attendances:
                    pass
            else:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_in', '<', attendance.check_out),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
              
    
    


    
    
    

