# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ReconciliationDetails(models.TransientModel):
    _name = "reconciliation.detail.wizard"
    _description = "Payroll Reconcile Report wizard"

    company_id = fields.Many2many('res.company', string='company')
    location_ids = fields.Many2many('hr.work.location', string='Location')
    department_ids = fields.Many2many('hr.department', string='department')
    cost_center_ids = fields.Many2many('account.analytic.account', string='cost center id')
    date_from = fields.Date(string='Date form', required=True)
    date_to = fields.Date(string='Date to', required=True)
    employee_type = fields.Selection([('permanent','Permanent'),('contractor','Contractor'),('freelancer','Freelancer'),('intern','Intern'),('part time','Part Time'),('project based hiring','Project Based Hiring'),('outsourse','Outsourse')])

    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from','date_to'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_from','date_to'])[0])
        return self.env.ref('de_payroll_reconcilation_report.open_payroll_reconciliation_detail_action').report_action(self, data=data, config=False)