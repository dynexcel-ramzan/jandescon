# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class HrLocationwise(models.TransientModel):
    _name = "ora.location.wise.wizard"
    _description = "HR Location Wise wizard"

    
    work_location_ids = fields.Many2many('hr.work.location', string='Location', required=True)

    def action_check_report(self):
        data = {}
        data['form'] = self.read(['work_location_ids'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['work_location_ids'])[0])
        return self.env.ref('de_employee_reports.hr_location_wise_report_xlx').report_action(self, data=data, config=False)