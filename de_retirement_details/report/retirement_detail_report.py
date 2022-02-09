import time
from odoo import api, models, _ , fields
from dateutil.parser import parse
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class EmployeeRetirementReport(models.AbstractModel):
    _name = 'report.de_retirement_details.report_employee_retirement_tem'
    _description = 'Employee Retirement Report'

    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env['retirement.wizard'].browse(self.env.context.get('active_id'))
        employee_retirement = self.env['hr.employee'].search([('date', '>=', docs.date_from), ('date', '<=', docs.date_to)])
        if docs.department_ids:
            employee_retirement = self.env['hr.employee'].search(
                [('date', '>=', docs.date_from), ('date', '<=', docs.date_to),
                 ('department_id', 'in', docs.department_ids.ids)])
        if docs.location_ids:
            employee_retirement = self.env['hr.employee'].search(
                [('date', '>=', docs.date_from), ('date', '<=', docs.date_to),
                 ('employee_id.work_location_id', 'in', docs.location_ids.ids)])
        if docs.company_id:
            employee_retirement = self.env['hr.employee'].search(
                [('date', '>=', docs.Date_from), ('date', '<=', docs.Date_to),
                 ('res.company', 'in', docs.company_id)])
        if docs.employee_type:
            employee_retirement = self.env['hr.employee'].search(
                [('date', '>=', docs.Date_from), ('date', '<=', docs.Date_to),
                 ('employee_id.emp_type', 'in', docs.employee_type)])

        return {
            'employee_retirement': employee_retirement,
            'docs': docs,
        }



