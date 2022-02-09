# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class LeaveLedgerWizard(models.TransientModel):
    _name = "leave.ledger.wizard"
    _description = "Leave Ledger wizard"

    employee_ids = fields.Many2many('hr.employee', string='Employee')
    start_date = fields.Date(string='From Date', required='1', help='select start date')
    end_date = fields.Date(string='To Date', required='1', help='select end date')
    
    
    @api.model
    def default_get(self, fields_list):
        # OVERRIDE
        res = super().default_get(fields_list)
        req = self.env['hr.leave.type'].sudo().search([('fiscal_year','=',fields.date.today().year),('validity_stop','!=',False),('validity_start','!=',False)], limit=1)
        res['start_date']= req.validity_start
        res['end_date']= req.validity_stop
        return res
    
    def check_report(self):
        data = {}
        data['form'] = self.read(['start_date', 'end_date','employee_ids'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['start_date', 'end_date','employee_ids'])[0])
        return self.env.ref('de_leave_portal.open_leave_ledger_wizard_action').report_action(self, data=data, config=False)