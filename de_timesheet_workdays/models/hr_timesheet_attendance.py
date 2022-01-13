# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class HrTimesheetAttendance(models.Model):
    _name = 'hr.timesheet.attendance'
    _description = 'HR Timesheet Attendance'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    check_in = fields.Datetime(string='Check In', required=True)
    check_out = fields.Datetime(string='Check Out')
    total_duration = fields.Float(string='Total Hours', compute='compute_total_hours')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
         ],
        readonly=True, string='Status', default='draft')
    approval_request_id = fields.Many2one('approval.request', string="Approval")
    category_id = fields.Many2one(related='employee_id.category_id')
    emp_number = fields.Char(related='employee_id.emp_number')
    department_id = fields.Many2one(related='employee_id.department_id')
    grade_type_id = fields.Many2one(related='employee_id.grade_type')
    timesheet_attendance_ids = fields.One2many('hr.timesheet.attendance.line', 'timesheet_att_id', string='Timesheet Attendace Line')
    
    def action_submit(self):
        for line in self:
            line.update({
                'state': 'submitted'
            })
            line.action_create_approval_request_attendance()
    
    def action_approved(self):
        for line in self:
            for sheet_line in line.timesheet_attendance_ids:
                timesheet_vals = {
                    'date': sheet_line.timesheet_att_id.check_in,
                    'employee_id': sheet_line.timesheet_att_id.employee_id.id,
                    'project_id':  sheet_line.project_id.id,
                    'task_id': sheet_line.task_id.id,
                    'name': sheet_line.description,
                    'unit_amount': sheet_line.duration,
                }
                timesheet = self.env['account.analytic.line'].sudo().create(timesheet_vals)
            attendance_vals = {
                'employee_id': line.employee_id.id,
                'check_in': line.check_in,
                'check_out': line.check_out,
                'att_date': line.check_out,
            } 
            attendance = self.env['hr.attendance'].sudo().create(attendance_vals)
            line.update({
                'state': 'approved'
            })
    
    def action_refuse(self):
        for line in self:
            line.update({
                'state': 'refused'
            })
    
    
    @api.depends('timesheet_attendance_ids.duration')
    def compute_total_hours(self):
        for line in self:
            tot_hours = 0.0
            for sheet_line in line.timesheet_attendance_ids:
                tot_hours += sheet_line.duration     
            line.update({
                'total_duration':  tot_hours,
            }) 
            if line.check_in:
                line.update({
                    'check_out':  line.check_in + relativedelta(hours =+ tot_hours)
                }) 
            
    def action_create_approval_request_attendance(self):
        approver_ids  = []       
        request_list = []
        for line in self:
            check_in = False
            check_out = False
            if line.check_in:
                check_in = line.check_in + relativedelta(hours =+ 5)
            if line.check_out:
                check_out = line.check_out + relativedelta(hours =+ 5)
            if line.category_id:
                request_list.append({
                        'name':  str(line.employee_id.name ),
                        'request_owner_id': line.employee_id.user_id.id,
                        'category_id': line.category_id.id,
                        'timesheet_att_id': line.id,
                        'reason': ' Employee: ' + str(line.employee_id.name)+"\n",
                        'request_status': 'new',
                })
                approval_request_id = self.env['approval.request'].create(request_list)
                approval_request_id._onchange_category_id()
                approval_request_id.action_confirm()
                approval_request_id.action_date_confirm_update()
                line.approval_request_id = approval_request_id.id        
    
    
    
class HrTimesheetLine(models.Model):
    _name = 'hr.timesheet.attendance.line'
    _description = 'HR Timesheet Attendance'
    _rec_name = 'project_id'
    
    project_id = fields.Many2one('project.project', string='Project', required=True)
    task_id = fields.Many2one('project.task', string='Task')
    duration = fields.Float(string='Duration')
    description = fields.Char(string='Description')
    timesheet_att_id = fields.Many2one('hr.timesheet.attendance', string='Timesheet Attendace')
    
        
    
    

