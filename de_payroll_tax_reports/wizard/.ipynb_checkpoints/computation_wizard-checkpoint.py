# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta



class TaxComputationWizard(models.Model):
    _name = 'tax.computation.wizard'
    _description = 'Tax Computation Wizard'
     

    company_id = fields.Many2one('res.company',  string='Company', required=True)
    company_number = fields.Integer(string='Company Code')
    employee_id = fields.Many2one('hr.employee',  string='Employee', required=True, domain='[("company_id","=",company_id)]')
    date_from =  fields.Date(string='Month From', required=True)
    date_to =  fields.Date(string='Month To', required=True)
    
    @api.onchange('company_id')
    def onchange_company(self):
        for line in self:
            if line.company_id:
                line.company_number =line.company_id.segment1
                fiscal_month_passed = 0
                if (line.company_id.fiscal_month.id > fields.date.today().month):
                    fiscal_month_passed = (line.company_id.fiscal_month.id - fields.date.today().month)
                else: 
                    fiscal_month_passed = (fields.date.today().month - line.company_id.fiscal_month.id)
                date_from = fields.date.today() - timedelta(fiscal_month_passed*30)
                line.date_from = date_from
                line.date_to = fields.date.today()
                
    @api.onchange('company_number')
    def onchange_company_number(self):
        for line in self:
            if line.company_number:
                line.company_id =self.env['res.company'].search([('segment1','=',line.company_number)], limit=1).id
    
    
    def check_report(self):
        data = {}
        data['form'] = self.read(['company_id','date_from', 'date_to','employee_id'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['company_id','date_from', 'date_to','employee_id'])[0])
        return self.env.ref('de_payroll_tax_reports.open_tax_computation_action').report_action(self, data=data, config=False)
