# -*- coding: utf-8 -*-

from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.osv import expression
from odoo.exceptions import UserError
from collections import OrderedDict
from datetime import date, datetime, timedelta
from operator import itemgetter
from datetime import datetime , date
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR

class HrTimesheetReport(models.AbstractModel):
    _name = 'report.de_portal_timesheet.timesheet_report'
    _description = 'Hr Timesheet Report'

    
    def _get_report_values(self, docids, data=None):
        timesheet_list = []
        date_from = datetime.strptime(str(data['start_date']), "%Y-%m-%d")
        date_to = datetime.strptime(str(data['end_date']), "%Y-%m-%d")
        project= self.env['project.project'].search([('id','=',data['project'])])
        incharge= self.env['hr.employee'].search([('id','=',data['employee'])])
        timesheets_date_in=self.env['hr.timesheet.report.line'].sudo().search([('project_id','=',data['project']),('timesheet_repo_id.incharge_id','=',data['employee']),('date_from','>=',data['start_date']),('date_from','<=',data['end_date'])])
        timesheets_date_out=self.env['hr.timesheet.report.line'].sudo().search([('project_id','=',data['project']),('timesheet_repo_id.incharge_id','=',data['employee']),('date_to','>=',data['start_date']),('date_to','<=',data['end_date'])])
        timesheets=self.env['hr.timesheet.report.line'].sudo().search([('project_id','=',data['project']),('timesheet_repo_id.incharge_id','=',data['employee']),('date_from','>=',data['start_date']),('date_to','<=',data['end_date'])])
        delta_days = (date_to - date_from).days+1
        employee_list = []
        for line in timesheets:
            employee_list.append(line.employee_id.id)
        for line_in in timesheets_date_in:
            employee_list.append(line_in.employee_id.id)
        for line_out in timesheets_date_out:
            employee_list.append(line_out.employee_id.id)
        uniq_employee_list = set(employee_list) 
        start_date_from = date_from
        line_date_from = date_from
        for uniq_employee in uniq_employee_list:
            for day in range(delta_days):
                initialize_start_date = (date_from + timedelta(day))
                start_date_from = (date_from + timedelta(day)).strftime('%Y-%m-%d')
                timesheet = 'N/A'
                overtime = 0
                shift_hours = 0
                attendance_hours = 0
                rest_day = "0"
                ggazetted_day = "0"
                shift_line=self.env['hr.shift.schedule.line'].search([('employee_id','=',uniq_employee),('date','=',start_date_from),('state','=','posted'),('rest_day','=',True)], limit=1)
                if shift_line:
                    rest_day = "1"
                employee=self.env['hr.employee'].search([('id','=',uniq_employee)], limit=1)    
                shift = self.env['resource.calendar'].search([('company_id','=',employee.company_id.id),('shift_type','=','general')], limit=1)   
                gazeted_shift_line=self.env['hr.shift.schedule.line'].search([('employee_id','=',uniq_employee),('date','=',start_date_from),('state','=','posted')], limit=1)
                if gazeted_shift_line.first_shift_id:
                    shift=gazeted_shift_line.first_shift_id
                for gazetted_day in shift.global_leave_ids:
                    gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                    gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                    if str(start_date_from) >= str(gazetted_date_from.strftime('%Y-%m-%d')) and str(start_date_from) <= str(gazetted_date_to.strftime('%Y-%m-%d')):
                        ggazetted_day = "1" 
                        
                # Constraints start        
                exist_timesheets=self.env['hr.timesheet.report.line'].sudo().search([('project_id','=',project.id),('employee_id','=',uniq_employee),('date_from','<=',start_date_from),('date_to','>=',start_date_from)], limit=1)
                if   exist_timesheets:  
                    attendances=self.env['hr.attendance'].search([('employee_id','=',uniq_employee),('check_in','!=', False),('check_out','!=',False),('att_date','=',start_date_from)])
                    for attend in  attendances:
                        attendance_hours += attend.worked_hours
                        shift_hours = attend.shift_id.hours_per_day
                    timesheet = ' '    
                    if (shift_hours/2) < attendance_hours :
                        timesheet = 'P'    
                    overtime_request=self.env['hr.overtime.request'].search([('employee_id','=',uniq_employee),('date_from','!=', False),('date_from','!=',False),('date','=',start_date_from),('state','=','approved')],limit=1)
                    if overtime_request:
                        overtime = overtime_request.overtime_hours
                                
                employee=self.env['hr.employee'].search([('id','=',uniq_employee)], limit=1)
                timesheet_list.append({
                    'id':  employee.id,
                    'timesheet': timesheet,
                    'date': start_date_from,
                    'overtime': round(overtime,2),
                    'rest_day': rest_day,
                    'gazetted_day': ggazetted_day,
                })
        return {
                'timesheet_list': timesheet_list,
                 'uniq_employee_list': uniq_employee_list, 
                 'date_from': date_from,
                 'partner': project.ora_client_id.name,
                 'project': project,
                 'incharge': incharge,
                 'date_to': date_to,
               }