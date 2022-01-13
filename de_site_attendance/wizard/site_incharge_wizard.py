
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SiteInchargeWizard(models.TransientModel):
    _name = "site.incharge.wizard"
    _description = "Site Attendance Incharge wizard"
    

    incharge_id = fields.Many2one('hr.employee', string='Incharge')    
    employee_ids = fields.Many2many('hr.employee', string='Employee')    
    
    def action_assign_incharge(self):
        for employee in self.employee_ids:
            employee.update({
                'site_incharge_id': self.incharge_id.id
            })
        
        