from odoo import models, fields, api, _
from datetime import datetime
from odoo import exceptions 
from odoo.exceptions import UserError, ValidationError 





class HrEmployee(models.Model):
    _inherit = 'hr.employee'
     
    allow_overtime = fields.Boolean(string='OT Allowed', )
    work_location_id = fields.Many2one('hr.work.location', string="Work Location", domain="[('company_id','=',company_id)]")
    cpl = fields.Boolean(string='CPL Gazetted/Rest Days')


    
    

