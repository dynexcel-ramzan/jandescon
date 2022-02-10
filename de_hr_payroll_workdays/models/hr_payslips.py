# -*- coding: utf-8 -*-

import base64
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips, ResultRules
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval
from datetime import date, datetime, timedelta

from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class HrPayslips(models.Model):
    _inherit = 'hr.payslip'
    
    
    
    @api.onchange('employee_id', 'struct_id', 'date_from', 'date_to')
    def _onchange_employee(self):        
        for payslip in self:            
            if (not payslip.employee_id) or (not payslip.date_from) or (not payslip.date_to):
                return

            employee = payslip.employee_id
            date_from = payslip.date_from
            date_to = payslip.date_to

            payslip.company_id = employee.company_id
            if not payslip.contract_id or payslip.employee_id != payslip.contract_id.employee_id: # Add a default contract if not already defined
                contracts = employee._get_contracts(date_from, date_to)

                if not contracts or not contracts[0].structure_type_id.default_struct_id:
                    payslip.contract_id = False
                    payslip.struct_id = False
                    return
                payslip.contract_id = contracts[0]
                payslip.struct_id = contracts[0].structure_type_id.default_struct_id

            lang = employee.sudo().address_home_id.lang or payslip.env.user.lang
            context = {'lang': lang}
            payslip_name = payslip.struct_id.payslip_name or _('Salary Slip')
            del context

            payslip.name = '%s - %s - %s' % (
                payslip_name,
                payslip.employee_id.name or '',
                format_date(self.env, payslip.date_to, date_format="MMMM y", lang_code=lang)
            )

            if date_to > date_utils.end_of(fields.Date.today(), 'month'):
                payslip.warning_message = _(
                    "This payslip can be erroneous! Work entries may not be generated for the period from %(start)s to %(end)s.",
                    start=date_utils.add(date_utils.end_of(fields.Date.today(), 'month'), days=1),
                    end=date_to,
                )
            else:
                payslip.warning_message = False 

            work_day_line = []    
            holiday = '0'
            delta_days = (date_to - date_from).days + 1
            start_date = date_from
            tot_hours = 0
            current_shift = self.env['resource.calendar'].search([('company_id','=',employee.company_id.id)], limit=1)
            attendance_day_count = 0
            rest_day_count = 0
            absent_day_count = 0
            leave_day_count = 0
            for dayline in range(delta_days):
                holiday = '0'
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
                    rest_day_count += 1
                for gazetted_day in current_shift.global_leave_ids:
                    gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                    gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                    if str(start_date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(start_date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')): 
                        holiday = '1'
                        rest_day_count += 1
                        remarks = str(gazetted_day.name)
                        if shift_line.rest_day==True:
                            rest_day_count -=1
                working_hours = 0
                exist_attendances=self.env['hr.attendance'].search([('employee_id','=',employee.id),('att_date','=',start_date)])
                leaves = self.env['hr.leave'].search([('employee_id','=',employee.id),('request_date_from','<=', start_date),('request_date_to','>=', start_date),('state','in',('confirm','validate'))])
                leave_total_days = 0
                leave_status = '' 
                for leave_day in leaves:
                    if leave_day.state=='validate':
                        leave_status = 'validate' 
                    elif leave_day.state=='confirm':
                        leave_status = 'confirm'  
                    leave_total_days += leave_day.number_of_days
                check_in_time = ''
                check_out_time = ''
                rectification = self.env['hr.attendance.rectification'].search([('employee_id','=',employee.id),('check_in','<=', start_date),('check_out','>=', start_date),('state','in',('submitted','approved'))], limit=1)
                for attendee in exist_attendances:
                    check_in_time = attendee.check_in
                    check_out_time = attendee.check_out
                    working_hours += attendee.worked_hours
                if   (working_hours > (current_shift.hours_per_day-1.5)):
                    attendance_day_count += 1
                    if holiday == '1':
                        rest_day_count -=1    
                elif (working_hours < (current_shift.hours_per_day-1.5)) and (working_hours >((current_shift.hours_per_day)/2)-1):
                    attendance_day_count += 0.5
                    if holiday != '1':
                        if rectification.state=='approved':
                            attendance_day_count += 0.5
                        elif leave_status=='validate' and leave_total_days >= 0.5:
                            leave_day_count += 0.5                            
                        elif leave_status=='validate' and leave_total_days == 0.25:
                            if working_hours < (((current_shift.hours_per_day-1)/4)*3):
                                leave_day_count += 0.25
                                absent_day_count += 0.25
                            else:
                                pass
                        elif rectification.state=='submitted':
                            absent_day_count = 0.5
                        elif not rectification and leave_status=='confirm':
                            if leave_total_days >= 0.5:
                                absent_day_count += 0.5
                            elif leave_total_days == 0.25:
                                absent_day_count += 0.5
                        else:
                             absent_day_count += 0.5 
                    else:
                        if holiday == '1': 
                            attendance_day_count -= 0.5  
                else:
                    if holiday != '1':
                        if rectification.state=='approved':
                            attendance_day_count += 1
                        elif leave_status=='validate' and leave_total_days >= 1:
                            leave_day_count += 1
                        elif rectification.state=='submitted':
                            absent_day_count += 1 
                        elif leave_status=='validate':
                            if leave_total_days >= 0.5:
                                leave_day_count += 0.5
                                absent_day_count += 0.5
                            else:
                                absent_day_count += 1
                        elif leave_status=='confirm':
                            if leave_total_days >= 1:
                                absent_day_count += 1
                            elif leave_total_days >= 0.5:
                                absent_day_count += 1
                            elif leave_total_days >= 0.25:
                                absent_day_count += 1 
                            else:
                                absent_day_count += 1 
                        else:
                            absent_day_count += 1  
                start_date = (start_date + timedelta(1))             
            if attendance_day_count >= 0:
                work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=','WORK100')], limit=1)
                if not work_entry_type:
                    vals = {
                        'name': 'Attendance Days',
                        'code': 'WORK100',
                        'round_days': 'NO',
                    }
                    work_entry_type = self.env['hr.work.entry.type'].sudo().create(vals)
                work_day_line.append((0,0,{
                   'work_entry_type_id' : work_entry_type.id ,
                   'name': work_entry_type.name ,
                   'sequence': work_entry_type.sequence ,
                   'number_of_days' : attendance_day_count ,
                   'number_of_hours' : round((attendance_day_count * current_shift.hours_per_day),2) ,
                }))
            if rest_day_count >= 0:
                work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=','REST100')], limit=1)
                if not work_entry_type:
                    vals = {
                        'name': 'Rest/Holiday Days',
                        'code': 'REST100',
                        'round_days': 'NO',
                    }
                    work_entry_type = self.env['hr.work.entry.type'].sudo().create(vals)
                work_day_line.append((0,0,{
                   'work_entry_type_id' : work_entry_type.id ,
                   'name': work_entry_type.name ,
                   'sequence': work_entry_type.sequence ,
                   'number_of_days' : rest_day_count ,
                   'number_of_hours' : round((rest_day_count * current_shift.hours_per_day),2) ,
                }))
            if leave_day_count >= 0:
                work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=','LEAVE100')], limit=1)
                if not work_entry_type:
                    vals = {
                        'name': 'Leave Days',
                        'code': 'LEAVE100',
                        'round_days': 'NO',
                    }
                    work_entry_type = self.env['hr.work.entry.type'].sudo().create(vals)
                work_day_line.append((0,0,{
                   'work_entry_type_id' : work_entry_type.id ,
                   'name': work_entry_type.name ,
                   'sequence': work_entry_type.sequence ,
                   'number_of_days' : leave_day_count ,
                   'number_of_hours' : round((leave_day_count * current_shift.hours_per_day),2),
                }))
            if absent_day_count >= 0:
                work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=','ABSENT100')], limit=1)
                if not work_entry_type:
                    vals = {
                        'name': 'Absent Days',
                        'code': 'ABSENT100',
                        'round_days': 'NO',
                    }
                    work_entry_type = self.env['hr.work.entry.type'].sudo().create(vals)
                work_day_line.append((0,0,{
                   'work_entry_type_id' : work_entry_type.id ,
                   'name': work_entry_type.name ,
                   'sequence': work_entry_type.sequence ,
                   'number_of_days' : absent_day_count ,
                   'number_of_hours' : round((absent_day_count * current_shift.hours_per_day),2) ,
                }))
            
            if payslip.worked_days_line_ids:
                payslip.worked_days_line_ids.unlink()
                payslip.worked_days_line_ids = work_day_line
            elif not payslip.worked_days_line_ids:
                payslip.worked_days_line_ids = work_day_line 


    