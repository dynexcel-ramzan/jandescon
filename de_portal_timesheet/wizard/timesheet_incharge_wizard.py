# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class TimesheetInchargeWizard(models.TransientModel):
    _name = "timesheet.incharge.wizard"
    _description = "Timesheet Incharge wizard"

    incharge_id = fields.Many2one('hr.employee', string='Incharge')
    employee_ids = fields.Many2many('hr.employee', string='Employee')

    def action_assign_incharge(self):
        for employee in self.employee_ids:
            employee.update({
                'timesheet_incharge_id': self.incharge_id.id
            })

