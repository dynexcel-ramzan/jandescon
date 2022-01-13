from odoo import models, api, fields, _


class HrRestDayConfig(models.Model):
    _name = 'hr.rest.day.config'
    
    name = fields.Char(string="Name")
    leave_type_id = fields.Many2one('hr.leave.type', string="Timeoff Type", required=True, domain="['|',('company_id','=',company_id),('company_id','=',False)]")
    company_id = fields.Many2one('res.company', string="Company", required=False, default=lambda self: self.env.company)

    
    
   
        
    
   