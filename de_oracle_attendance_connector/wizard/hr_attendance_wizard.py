import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class HrAttendanceProcess(models.Model):
    _name = 'attendance.process.wizard'
    _description = 'Attendance Process'
    
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date to') 
    is_filter = fields.Boolean(string='Is Date Filter')
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    
    def action_manually_process_att(self):
        employeelist = []
        delta_days = 30
        if self.is_filter == True:    
            delta_days = (self.date_to - self.date_from).days + 1
         
        user_attendance = self.env['hr.user.attendance']
        for emp in self.employee_ids:
            employeelist.append(emp.id)    
        user_attendance.action_attendace_validated(employeelist,delta_days)



class HrAttendanceWizard(models.TransientModel):
    _name = 'hr.attendance.wizard'
    _description = 'Attendance Wizard'

    @api.model
    def _get_all_device_ids(self):
        all_connectors = self.env['oracle.setting.connector'].search([('state', '=', 'active')])
        if all_connectors:
            return all_connectors.ids
        else:
            return []

    device_ids = fields.Many2many('oracle.setting.connector', string='Connector', default=_get_all_device_ids, domain=[('state', '=', 'active')])
    
   
    def cron_download_oracle_attendance(self):
        devices = self.env['oracle.setting.connector'].search([('state', '=', 'active')])
        for device in devices:
            device.action_get_attendance_data()

    def cron_process_oracle_attendance(self):
        devices = self.env['oracle.setting.connector'].search([('state', '=', 'active')])
        for device in devices:
            device.action_attendance_process()

    def cron_download_oracle_missing_attendance_a(self):
        devices = self.env['oracle.setting.connector'].search([('state', '=', 'active')])
        for device in devices:
            device.action_get_missing_attendance_data_a()

    def cron_download_oracle_missing_attendance_b(self):
        devices = self.env['oracle.setting.connector'].search([('state', '=', 'active')])
        for device in devices:
            device.action_get_missing_attendance_data_b()

    def cron_download_oracle_missing_attendance_c(self):
        devices = self.env['oracle.setting.connector'].search([('state', '=', 'active')])
        for device in devices:
            device.action_get_missing_attendance_data_c()

    
    def cron_download_oracle_missing_attendance_aa(self):
        devices = self.env['oracle.setting.connector'].search([('state', '=', 'active')])
        for device in devices:
            device.action_get_missing_attendance_data_aa()   

    def cron_download_oracle_missing_attendance_d(self):
        devices = self.env['oracle.setting.connector'].search([('state', '=', 'active')])
        for device in devices:
            device.action_get_missing_attendance_data_d() 

    def cron_download_oracle_missing_attendance_e(self):
        devices = self.env['oracle.setting.connector'].search([('state', '=', 'active')])
        for device in devices:
            device.action_get_missing_attendance_data_e()        
