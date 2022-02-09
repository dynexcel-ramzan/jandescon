 -*- coding: utf-8 -*-
import time
from odoo import api, models, _ , fields
from dateutil.parser import parse
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class EmployeeResignReport(models.AbstractModel):
    _name = 'report.de_employee_resigned_report.report_employee_resigned_tem'
    _description = 'Employee Resigned Report'
    
        def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env['resigned.wizard'].browse(self.env.context.get('active_id'))
        employee_resigned = self.env['hr.employee'].search([('date', '>=', docs.date_from), ('date', '<=', docs.date_to)])
        
         return {
            'employee_resigned': employee_resigned,
            'docs': docs,
        }
     