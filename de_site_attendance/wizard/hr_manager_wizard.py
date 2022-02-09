
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class HrManagerWizard(models.TransientModel):
    _name = "hr.manager.wizard"
    _description = "Manager wizard"
    

    manager_id = fields.Many2one('hr.employee', string='Incharge')    
    employee_ids = fields.Many2many('hr.employee', string='Employee')    
    
    def action_assign_manager(self):
        for employee in self.employee_ids:
            employee.update({
                'parent_id': self.manager_id.id
            })
        
        