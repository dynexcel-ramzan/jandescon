import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class ProcessAttendanceWizard(models.TransientModel):
    _name = 'process.attendance.wizard'
    _description = 'Process Attendance Wizard'
    
    
    
    process_number = fields.Integer(string='Process Number')
  
    
   
       
        
        
    def action_process_attendace_odoo(self):
        user_attendance = self.env['hr.user.attendance']
        user_attendance.action_process_attendace_validated(self.process_number)
        
   

