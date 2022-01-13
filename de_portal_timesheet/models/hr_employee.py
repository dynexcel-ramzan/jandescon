# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    timesheet_incharge_id = fields.Many2one('hr.employee', string='Timesheet Incharge')
    timesheet_categ_id = fields.Many2one('approval.category', string="Category", required=False)

    def action_assign_timesheet_incharge(self):
        for rec in self:
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['hr.employee'].browse(selected_ids)
        return {
            'name': ('Timesheet Incharge'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'timesheet.incharge.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_employee_ids': selected_records.ids},
        }
