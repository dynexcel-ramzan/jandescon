import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


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
    # DCL    
        
    def cron_hr_user_attendance_validate_dcl(self):
        user_attendance = self.env['hr.user.attendance']
        user_attendance.action_attendace_validated_dcl()
    
    
    #   Rousch Pakistan Power Limited
    
    def action_attendace_validated_rousch(self):
        user_attendance = self.env['hr.user.attendance']
        user_attendance.action_attendace_validated_rousch()    
        
   
        #   Inspectest (Pvt) Limited
    
    def action_attendace_validated_ipl(self):
        user_attendance = self.env['hr.user.attendance']
        user_attendance.action_attendace_validated_ipl()    
        
    #   Gray Mackenzie Engineering Services W.L.L
    
    def action_attendace_validated_dmesw(self):
        user_attendance = self.env['hr.user.attendance']
        user_attendance.action_attendace_validated_dmesw()    
        
       
        #   Gray Mackenzie Engineering Services LLC
    
    def action_attendace_validated_gmesl(self):
        user_attendance = self.env['hr.user.attendance']
        user_attendance.action_attendace_validated_gmesl()    
        
        #   Descon Technical Institute
    
    def action_attendace_validated_dti(self):
        user_attendance = self.env['hr.user.attendance']
        user_attendance.action_attendace_validated_dti()    
            
    #   Descon Power Solutions (Private) Limited
    
    def action_attendace_validated_dps(self):
        user_attendance = self.env['hr.user.attendance']
        user_attendance.action_attendace_validated_dps()    
        
    #   Descon Oxychem Limited
    
    def action_attendace_validated_dol(self):
        user_attendance = self.env['hr.user.attendance']
        user_attendance.action_attendace_validated_dol()    
        
    #   Altern Energy Limited

    
    def action_attendace_validated_ael(self):
        user_attendance = self.env['hr.user.attendance']
        user_attendance.action_attendace_validated_ael()    
                