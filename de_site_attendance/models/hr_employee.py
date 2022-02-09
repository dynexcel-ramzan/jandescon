from odoo import api, fields, models, _
from calendar import monthrange

from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    site_incharge_id = fields.Many2one('hr.employee', string="Incharge")
    site_user_id = fields.Many2one(related='site_incharge_id.user_id', string="Incharge User")
    
    def action_assign_incharge(self):
        for rec in self:
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['hr.employee'].browse(selected_ids)
        return {
            'name': ('Attendance Incharge'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'site.incharge.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_employee_ids': selected_records.ids},
        }
    
    def action_assign_manager(self):
        for rec in self:
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['hr.employee'].browse(selected_ids)
        return {
            'name': ('Manager'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.manager.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_employee_ids': selected_records.ids},
        }
        
    

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'
  