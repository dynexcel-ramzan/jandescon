import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class HrOvertimeAllocate(models.TransientModel):
    _name = 'hr.overtime.allocate'
    _description = 'Hr Overtime Allocate Wizard'

    date_start = fields.Datetime(string='Date From')
    date_end = fields.Datetime(string='Date To')
    
    def action_create_overtime(self):
        attendance = self.env['hr.attendance']
        attendance.cron_create_overtime()
    
    
    def action_allocate_overtime(self):
        day_min_ovt = 0
        day_max_ovt = 0
        month_min_ovt = 0
        month_max_ovt = 0
        overtime_rule = self.env['hr.overtime.rule'].search([])
        for rule in overtime_rule:
            if rule.rule_period == 'day' and rule.rule_type == 'minimum':
                day_min_ovt == rule.hours   
            elif rule.rule_period == 'day' and rule.rule_type == 'maximum':
                day_max_ovt = rule.hours 
            elif rule.rule_period == 'month' and rule.rule_type == 'minimum':
                month_min_ovt = rule.hours   
            elif rule.rule_period == 'month' and rule.rule_type == 'maximum':
                month_max_ovt = rule.hours     
                
        employees = self.env['hr.employee'].search([('allow_overtime','=',True)])
        for employee in employees:
            month_ovt_hours = 0
            month_total_hours = 0
            attendance_ids = []
            overtime_request = self.env['hr.overtime.request'].search([('employee_id','=', employee.id),('date','>=',self.date_start),('date','<=',self.date_end)])
            ovt_hours = 0
            for ovt_req in overtime_request:
                ovt_hours  = ovt_hours + ovt_req.overtime_hours   
            if ovt_hours < month_max_ovt:
                employee_attendance = self.env['hr.attendance'].search([('is_overtime','=',False),('employee_id','=',employee.id),('check_in','>=',self.date_start),('check_in','<=',self.date_end)])
                for attendance in employee_attendance:                    
                    overtime_limit = 0
                    month_total_hours = month_total_hours +  attendance.worked_hours   
                    overtime_limit = attendance.worked_hours - employee.shift_id.hours_per_day    
                    if overtime_limit > day_min_ovt:
                        month_ovt_hours = month_ovt_hours +  overtime_limit
                        attendance.update({
                        'is_overtime': True
                        })  

                        attendance_ids.append(attendance.id)
                request_date = self.date_start
                ovt_request_date = request_date.strftime('%Y-%m-%d')
                if month_ovt_hours > 0:
                    vals = {
                                'employee_id': employee.id,
                                'date':  ovt_request_date,
                                'date_from': self.date_start,
                                'date_to': self.date_end,
                                'hours': month_total_hours,
                                'overtime_hours': month_ovt_hours,
                            }
                    overtime_lines = self.env['hr.overtime.request'].create(vals)     

