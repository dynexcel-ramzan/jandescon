# -*- coding: utf-8 -*-
import time
from odoo import api, models, _ , fields 
from dateutil.parser import parse
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class LeaveLedgerReport(models.AbstractModel):
    _name = 'report.de_leave_portal.leave_ledger_report'
    _description = 'Leave Ledger Report'
    
    
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        
        return {
                'docs': docs,
                'employees_ledgers': docs.employee_ids,
                'date_from': datetime.strptime(str(docs.start_date), "%Y-%m-%d").strftime('%Y-%m-%d'),
                'date_to': datetime.strptime(str(docs.end_date), "%Y-%m-%d").strftime('%Y-%m-%d'),
                'req_date_from': docs.start_date,
                'req_date_to': docs.end_date,
               }    
    
    
class LeaveLedgerPortal(models.AbstractModel):
    _name = 'report.de_leave_portal.leave_ledger_portal'
    _description = 'Leave Ledger Portal'
    
    
    def _get_report_values(self, docids, data=None):
        employees = self.env['hr.employee'].sudo().search([('id','=', data['employee'])], limit=1)
        return {
                'docs': data,
                'employees_ledgers': employees,
                'date_from': datetime.strptime(str(data['start_date']), "%Y-%m-%d").strftime('%Y-%m-%d'),
                'date_to': datetime.strptime(str(data['end_date']), "%Y-%m-%d").strftime('%Y-%m-%d'),
                'req_date_from': datetime.strptime(str(data['start_date']), "%Y-%m-%d"),
                'req_date_to': datetime.strptime(str(data['end_date']), "%Y-%m-%d"),
               }        