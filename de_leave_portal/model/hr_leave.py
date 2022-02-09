# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

    


    
class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'      
    
    
    is_publish = fields.Boolean(string="Publish At Website")
    

class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'
    

class ResourceCalanderLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'    


    

    

class ResourceCalanderAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'  
            

class ResourceResource(models.Model):
    _inherit = 'resource.resource' 
    
class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'  
                
            


    