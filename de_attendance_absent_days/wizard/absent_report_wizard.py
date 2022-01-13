from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AbsentReport(models.TransientModel):
    _name = 'absent.report.wizard'
    _description = 'Absent Report Wizard'

    company_ids = fields.Many2many('res.company', string='Company')
    date_from= fields.Date(string='Date from', required=True)
    date_to = fields.Date(string='Date to', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Employee')
    
    def print_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to','employee_ids'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to','employee_ids'])[0])
        return self.env.ref('de_attendance_absent_days.absent_report_xlx').report_action(self, data=data, config=False)