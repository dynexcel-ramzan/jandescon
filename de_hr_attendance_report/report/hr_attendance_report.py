# -*- coding: utf-8 -*-
import time
from odoo import api, models, _ , fields 
from dateutil.parser import parse
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class HrAttendanceReport(models.AbstractModel):
    _name = 'report.de_hr_attendance_report.attendance_report'
    _description = 'Hr Attendance Report'
  
    
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        employees_attendance = []
        portal_employee = []
        for employee11 in docs.employee_ids:
            work_day_line = [] 
            employee = self.env['hr.employee'].sudo().search([('id','=', employee11.id)], limit=1)
            attendances = []
            remarks = 'Absent'
            holiday = '0'
            rest_day = '0'
            absent = '1'
            delta_days = (docs.end_date - docs.start_date).days + 1
            start_date = docs.start_date
            tot_hours = 0
            rest_day = 'N'
            attendance_day_count = 0
            rest_day_count = 0
            absent_day_count = 0
            leave_day_count = 0
            for dayline in range(delta_days):
                holiday = '0'
                remarks = 'Absent'
                absent = '1'
                rest_day = 'N'
                current_shift = self.env['resource.calendar'].search([('company_id','=',employee.company_id.id)], limit=1)
                if employee.shift_id: 
                    current_shift = employee.shift_id 
                shift_line=self.env['hr.shift.schedule.line'].sudo().search([('employee_id','=',employee.id),('date','=',start_date),('state','=','posted')], limit=1)
                if shift_line.first_shift_id:
                    current_shift = shift_line.first_shift_id
                elif shift_line.second_shift_id:
                    current_shift = shift_line.second_shift_id   
                if shift_line.rest_day==True:
                    holiday = '1'
                    rest_day = 'Y'
                    absent = '0'
                    rest_day_count += 1
                    remarks = 'Rest Day'
                for gazetted_day in current_shift.global_leave_ids:
                    gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                    gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                    if str(start_date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(start_date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')): 
                        holiday = '1'
                        rest_day = 'Y'
                        absent = '0'
                        rest_day_count += 1
                        remarks = str(gazetted_day.name)
                        if shift_line.rest_day==True:
                            rest_day_count -=1
                working_hours = 0
                exist_attendances=self.env['hr.attendance'].search([('employee_id','=',employee.id),('att_date','=',start_date)])
                leaves = self.env['hr.leave'].search([('employee_id','=',employee.id),('request_date_from','<=', start_date),('request_date_to','>=', start_date),('state','in',('confirm','validate'))])
                check_in_time = ''
                check_out_time = ''
                leave_number_of_days = 0
                leave_status = ''
                for leave_day in leaves:
                    if leave_day.state=='validate':
                        leave_status = 'validate'    
                    elif leave_day.state=='confirm':
                        leave_status = 'confirm'                       
                    leave_number_of_days += leave_day.number_of_days
                rectification = self.env['hr.attendance.rectification'].search([('employee_id','=',employee.id),('check_in','<=', start_date),('check_out','>=', start_date),('state','in',('submitted','approved'))], limit=1)
                for attendee in exist_attendances:
                    check_in_time = attendee.check_in
                    check_out_time = attendee.check_out    
                    if attendee.check_in:
                        check_in_time = attendee.check_in + relativedelta(hours=+5)
                    if attendee.check_out: 
                        check_out_time = attendee.check_out + relativedelta(hours=+5)
                    working_hours += attendee.worked_hours
                if (working_hours > (current_shift.hours_per_day-1.5)):
                    remarks = 'Attendance Present'
                    attendance_day_count += 1
                    absent = '0'
                    if holiday == '1':
                        rest_day_count -= 1    
                elif (working_hours < (current_shift.hours_per_day-1.5)) and (working_hours > ((current_shift.hours_per_day)/2)-1.5):
                    attendance_day_count += 0.5
                    remarks = 'Half Present'
                    if holiday != '1':
                        if rectification.state=='approved':
                            remarks = 'Rectification (Approved)'
                            absent = '0'
                            attendance_day_count += 0.5
                        elif leave_status=='validate' and leave_number_of_days >= 0.5:
                            remarks = 'Leave (Approved)[0.5]'
                            leave_day_count += 0.5
                            absent = '0'
                        elif leave_status=='validate' and leave_number_of_days == 0.25:
                            remarks = 'Half Present (Leave[Approved] (0.25))'
                            if working_hours < (((current_shift.hours_per_day-1.5)/4)*3):
                                absent = '1'
                                absent_day_count += 0.25 
                                leave_day_count += 0.25   
                            else:
                                remarks = 'Attendance Present (Leave[Approved] (0.25))' 
                                attendance_day_count += 0.25
                                absent = '0'           
                        elif rectification.state=='submitted':
                            absent = '1'
                            remarks = 'Half Present (Rectification [To Approve])'
                            absent_day_count = 0.5
                        elif not rectification and leave_status=='confirm':
                            if leave_number_of_days >= 0.5:
                                absent = '1'
                                remarks = 'Half Present (Leave [To Approve] (0.5))'
                                absent_day_count += 0.5
                            elif leave_number_of_days == 0.25:
                                absent = '1'
                                remarks = 'Half Present (Leave [To Approve] (0.25))'
                                absent_day_count += 0.5
                            else:
                                absent = '1'
                                absent_day_count += 0.5     
                        else:
                             absent = '1'
                             absent_day_count += 0.5  
                    else:
                        if holiday == '1': 
                            attendance_day_count -= 0.5 
                
                else:
                    if holiday == '0':
                        if rectification.state=='approved':
                            remarks = 'Rectification (Approved)'
                            attendance_day_count += 1
                            absent = '0'
                        elif leave_status=='validate' and leave_number_of_days >= 1:
                            remarks = 'Leave (Approved)'
                            leave_day_count += 1
                            absent = '0'
                        elif rectification.state=='submitted':
                            absent = '1'
                            remarks = 'Rectification (To Approve)'
                            absent_day_count += 1
                        elif leave_status=='confirm':
                            if leave_number_of_days >= 1:
                                absent = '1'
                                remarks = 'Leave (To Approve)'
                                absent_day_count += 1
                            elif leave_number_of_days >= 0.5:
                                absent = '1'
                                remarks = 'Half Leave (To Approve) (0.5)'
                                absent_day_count += 1 
                            elif leave_number_of_days >= 0.25:
                                absent = '1'
                                remarks = 'Short Leave (To Approve) (0.25)'
                                absent_day_count += 1
                            else:
                                absent = '1'
                                absent_day_count += 1
                        elif leave_status=='validate':
                            if leave_number_of_days >= 0.5:
                                absent = '1'
                                remarks = 'Half Leave (Approved) (0.5)'
                                leave_day_count += 0.5
                                absent_day_count += 0.5
                            elif leave_number_of_days >= 0.25:
                                absent = '1'
                                remarks = 'Short Leave (Approved) (0.25)'
                                leave_day_count += 0.25
                                absent_day_count += 0.75  
                            else:
                                absent = '1'
                                absent_day_count += 1    
                        else:
                            absent = '1'
                            absent_day_count += 1   
                attendances.append({
                    'date': start_date.strftime('%d/%b/%Y'),
                    'day':  start_date.strftime('%A'),
                    'check_in': check_in_time.strftime('%d/%b/%Y %H:%M:%S') if check_in_time else '',
                    'check_out':  check_out_time.strftime('%d/%b/%Y %H:%M:%S') if check_out_time else '',
                    'hours': working_hours,
                    'shift': current_shift.name,
                    'holiday': holiday,
                    'absent': absent,
                    'rest_day': rest_day,
                    'remarks': remarks,
                }) 
                start_date = (start_date + timedelta(1))   
            employees_attendance.append({
                'name': employee.name,
                'employee_no': employee.emp_number,
                'attendances': attendances,
                'attendance_day_count': attendance_day_count,
                'rest_day_count': rest_day_count,
                'absent_day_count': absent_day_count,
                'leave_day_count': leave_day_count,
            }) 
        return {
                'employee': docs,
                'employees_attendance': employees_attendance,
                'date_from': datetime.strptime(str(docs.start_date), "%Y-%m-%d").strftime('%Y-%m-%d'),
                'date_to': datetime.strptime(str(docs.end_date), "%Y-%m-%d").strftime('%Y-%m-%d'),
               }
        


        
# #  portal Report


class PortalAttendanceReport(models.AbstractModel):
    _name = 'report.de_hr_attendance_report.attendance_report_portal'
    _description = 'Hr Attendance Report'

    
    
    
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        employees_attendance = []
        portal_employee = []
        portal_employee.append(data['employee'])
        
        for employee11 in portal_employee:
            work_day_line = [] 
            employee = self.env['hr.employee'].sudo().search([('id',
                                                       '=', employee11)], limit=1)
            date_from = datetime.strptime(str(data['start_date']), "%Y-%m-%d")
            date_to = datetime.strptime(str(data['end_date']), "%Y-%m-%d")
            req_date_from = data['start_date']
            req_date_to = data['end_date']
            attendances = []
            remarks = 'Absent'
            holiday = '0'
            rest_day = '0'
            absent = '1'
            delta_days = (date_to - date_from).days + 1
            start_date = date_from
            tot_hours = 0
            rest_day = 'N'
            attendance_day_count = 0
            rest_day_count = 0
            absent_day_count = 0
            leave_day_count = 0
            for dayline in range(delta_days):
                holiday = '0'
                remarks = 'Absent'
                absent = '1'
                rest_day = 'N'
                current_shift = self.env['resource.calendar'].search([('company_id','=',employee.company_id.id)], limit=1)
                if employee.shift_id: 
                    current_shift = employee.shift_id 
                shift_line=self.env['hr.shift.schedule.line'].sudo().search([('employee_id','=',employee.id),('date','=',start_date),('state','=','posted')], limit=1)
                if shift_line.first_shift_id:
                    current_shift = shift_line.first_shift_id
                elif shift_line.second_shift_id:
                    current_shift = shift_line.second_shift_id   
                if shift_line.rest_day==True:
                    holiday = '1'
                    rest_day = 'Y'
                    absent = '0'
                    rest_day_count += 1
                    remarks = 'Rest Day'
                for gazetted_day in current_shift.global_leave_ids:
                    gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                    gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                    if str(start_date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(start_date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')): 
                        holiday = '1'
                        rest_day = 'Y'
                        absent = '0'
                        rest_day_count += 1
                        remarks = str(gazetted_day.name)
                        if shift_line.rest_day==True:
                            rest_day_count -=1
                working_hours = 0
                exist_attendances=self.env['hr.attendance'].search([('employee_id','=',employee.id),('att_date','=',start_date)])
                leaves = self.env['hr.leave'].search([('employee_id','=',employee.id),('request_date_from','<=', start_date),('request_date_to','>=', start_date),('state','in',('confirm','validate'))])
                check_in_time = ''
                check_out_time = ''
                leave_number_of_days = 0
                leave_status = ''
                for leave_day in leaves:
                    if leave_day.state=='validate':
                        leave_status = 'validate'    
                    elif leave_day.state=='confirm':
                        leave_status = 'confirm'  
                    leave_number_of_days += leave_day.number_of_days                          
                rectification = self.env['hr.attendance.rectification'].search([('employee_id','=',employee.id),('check_in','<=', start_date),('check_out','>=', start_date),('state','in',('submitted','approved'))], limit=1)
                for attendee in exist_attendances:
                    check_in_time = attendee.check_in
                    check_out_time = attendee.check_out    
                    if attendee.check_in:
                        check_in_time = attendee.check_in + relativedelta(hours=+5)
                    if attendee.check_out: 
                        check_out_time = attendee.check_out + relativedelta(hours=+5)
                    working_hours += attendee.worked_hours
                if   (working_hours > (current_shift.hours_per_day-1.5)):
                    remarks = 'Attendance Present'
                    attendance_day_count += 1
                    absent = '0'
                    if holiday == '1':
                        rest_day_count -= 1     
                elif (working_hours < (current_shift.hours_per_day-1.5)) and (working_hours >((current_shift.hours_per_day)/2)-1.5):
                    attendance_day_count += 0.5
                    remarks = 'Half Present'    
                    if holiday != '1':
                        if rectification.state=='approved':
                            remarks = 'Rectification (Approved)'
                            absent = '0'
                            attendance_day_count += 0.5
                        elif leave_status=='validate' and leave_number_of_days >= 0.5:
                            remarks = 'Leave (Approved)[0.5]'
                            leave_day_count += 0.5
                            absent = '0'
                            
                        elif leave_status=='validate' and leave_number_of_days == 0.25:
                            remarks = 'Half Present (Leave[Approved] (0.25))'
                            if working_hours < (((current_shift.hours_per_day-1.5)/4)*3):
                                absent = '1'
                                leave_day_count += 0.25
                                absent_day_count += 0.25
                            else:
                                remarks = 'Attendance Present (Leave[Approved] (0.25))' 
                                attendance_day_count += 0.25
                                absent = '0'
                        elif rectification.state=='submitted':
                            absent = '1'
                            remarks = 'Half Present (Rectification [To Approve])'
                            absent_day_count = 0.5
                        elif not rectification and leave_status=='confirm':
                            if leave_number_of_days >= 0.5:
                                absent = '1'
                                remarks = 'Half Present (Leave [To Approve] (0.5))'
                                absent_day_count += 0.5
                            elif leave_number_of_days == 0.25:
                                absent = '1'
                                remarks = 'Half Present (Leave [To Approve] (0.25))'
                                absent_day_count += 0.5
                            else:
                                absent = '1'
                                absent_day_count += 1 
                        else:
                             absent = '1'
                             absent_day_count += 0.5
                    else:
                        if holiday == '1': 
                            attendance_day_count -= 0.5   
                else:
                    if holiday != '1':
                        if rectification.state=='approved':
                            remarks = 'Rectification (Approved)'
                            attendance_day_count += 1
                            absent = '0'
                        elif leave_status=='validate' and leave_number_of_days >= 1:
                            remarks = 'Leave (Approved)'
                            leave_day_count += 1
                            absent = '0'
                        elif rectification.state=='submitted':
                            absent = '1'
                            remarks = 'Rectification (To Approve)'
                            absent_day_count += 1
                        elif leave_status=='confirm':
                            if leave_number_of_days >= 1:
                                absent = '1'
                                remarks = 'Leave (To Approve)'
                                absent_day_count += 1
                            elif leave_number_of_days >= 0.5:
                                absent = '1'
                                remarks = 'Half Leave (To Approve) (0.5)'
                                absent_day_count += 1 
                            elif leave_number_of_days >= 0.25:
                                absent = '1'
                                remarks = 'Short Leave (To Approve) (0.25)'
                                absent_day_count += 1
                            else:
                                absent = '1'
                                absent_day_count += 1
                        elif leave_status=='validate':
                            if leave_number_of_days >= 0.5:
                                absent = '1'
                                remarks = 'Half Leave (Approved) (0.5)'
                                leave_day_count += 0.5
                                absent_day_count += 0.5
                            elif leave_number_of_days >= 0.25:
                                absent = '1'
                                remarks = 'Short Leave (Approved) (0.25)'
                                leave_day_count += 0.25
                                absent_day_count += 0.75
                            else:
                                absent = '1'
                                absent_day_count += 1     
                        else:
                            absent = '1'
                            absent_day_count += 1   
                attendances.append({
                    'date': start_date.strftime('%d/%b/%Y'),
                    'day':  start_date.strftime('%A'),
                    'check_in': check_in_time.strftime('%d/%b/%Y %H:%M:%S') if check_in_time else '',
                    'check_out':  check_out_time.strftime('%d/%b/%Y %H:%M:%S') if check_out_time else '',
                    'hours': working_hours,
                    'shift': current_shift.name,
                    'holiday': holiday,
                    'absent': absent,
                    'rest_day': rest_day,
                    'remarks': remarks,
                }) 
                start_date = (start_date + timedelta(1))   
            employees_attendance.append({
                'name': employee.name,
                'employee_no': employee.emp_number,
                'attendances': attendances,
                'attendance_day_count': attendance_day_count,
                'rest_day_count': rest_day_count,
                'absent_day_count': absent_day_count,
                'leave_day_count': leave_day_count,
            }) 
        
        return {
                'employees_attendance': employees_attendance,
                'date_from': datetime.strptime(str(data['start_date']), "%Y-%m-%d").strftime('%Y-%m-%d'),
                'date_to': datetime.strptime(str(data['end_date']), "%Y-%m-%d").strftime('%Y-%m-%d'),
               }
        
        
        
