# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class HrRecruitment(models.TransientModel):
    _name = "ora.retirement.wizard"
    _description = "HR Retirement wizard"
    
    employee_ids = fields.Many2many('hr.employee', string='Employee')
    start_date = fields.Date(string='Date From', required=True)
    end_date = fields.Date(string='Date To', required=True)

    def action_check_report(self):
        data = {}
        data['form'] = self.read(['start_date','end_date','employee_ids'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['start_date', 'end_date','employee_ids'])[0])
        return self.env.ref('de_employee_reports.hr_retirement_report_xlx').report_action(self, data=data, config=False)