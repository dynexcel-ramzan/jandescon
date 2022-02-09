from datetime import date, datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
from odoo import api, fields, models, _


class RetirementWizard(models.TransientModel):
    _name = 'retirement.wizard'
    _description = 'Retirement Wizard'

    date_from = fields.Date(string='Date from', required=True)
    date_to = fields.Date(string='Date to', required=True)
    department_ids = fields.Many2many('hr.department', string='department')
    location_ids = fields.Many2many('res.partner', string='Location')
    company_id = fields.Many2one('res.company', string='company')
    section = fields.Char(string="section")
    staff_type = fields.Many2one('hr.employee', string="Staff Type")
    employee_type = fields.Many2one('hr.employee', string="Employee Type")

    def action_check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to', 'department_ids', 'location_ids', 'employee_type', 'company_id', 'staff_type'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to', 'department_ids', 'location_ids', 'employee_type', 'company_id', 'staff_type'])[0])
        return self.env.ref('de_retirement_details.retirement_detail_report').report_action(self, data=data,
                                                                                            config=False)


