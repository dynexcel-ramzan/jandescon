# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class LeaveBalanceWizard(models.TransientModel):
    _name = "leave.balance.wizard"
    _description = "Leave Balance wizard"

    employee_ids = fields.Many2many('hr.employee', string='Employee')
    fiscal_year_id = fields.Many2one('ora.fiscal.year', string='Fiscal Year')
    

    def check_report(self):
        data = {}
        data['form'] = self.read(['fiscal_year_id','employee_ids'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['fiscal_year_id','employee_ids'])[0])
        return self.env.ref('de_employee_reports.leave_balance_report_xlx').report_action(self, data=data, config=False)