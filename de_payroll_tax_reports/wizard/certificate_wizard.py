# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta



class TaxCertificateWizard(models.Model):
    _name = 'tax.certificate.wizard'
    _description = 'Tax Certificate Wizard'

    company_id = fields.Many2one('res.company',  string='Company', required=True)
    company_number = fields.Integer(string='Company Code')
    employee_id = fields.Many2one('hr.employee',  string='Employee', required=True, domain='[("company_id","=",company_id)]')
    date_from =  fields.Date(string='Month From', required=True)
    date_to =  fields.Date(string='Month To', required=True)
    bank = fields.Char(string='Bank')
    branch = fields.Char(string='Branch/City')
    date_of_issue = fields.Date(string='Date of Issue', default=fields.date.today())
    section = fields.Char(string='Section #', default='under section 149 of Income Tax Ordinance, 2001 on account of')
    certificate_line_ids = fields.One2many('tax.certificate.wizard.line', 'certificate_id' , string='Certificate Lines')
    
    
    
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
        data['form'] = self.read(['company_id','date_from', 'date_to','employee_id','certificate_line_ids','bank','branch'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['company_id','date_from', 'date_to','employee_id','certificate_line_ids','bank','branch'])[0])
        return self.env.ref('de_payroll_tax_reports.open_tax_certificate_action').report_action(self, data=data, config=False)
    
    @api.onchange('date_from', 'date_to','employee_id','bank', 'branch')
    def onchange_date(self):
        for line in self:
            if line.date_from and line.date_to and line.employee_id and line.branch and line.bank:
                payslips=self.env['hr.payslip'].search([('employee_id','=',line.employee_id.id),('date_to','>=',line.date_from),('date_to','<=',line.date_to)])
                line.certificate_line_ids.unlink()
                for slip in payslips:
                    amount=0
                    for rule in slip.line_ids:
                        if rule.code=='INC01':
                            amount=rule.amount
                    vals = {
                        'period': slip.date_to.strftime('%b-%y'),
                        'bank':   line.bank,
                        'branch': line.branch,
                        'amount': round(amount),
                        'certificate_id': line.id,
                    }
                    certificate_line=self.env['tax.certificate.wizard.line'].create(vals)

    
class TaxCertificateWizardline(models.Model):
    _name = 'tax.certificate.wizard.line'
    _description = 'Tax Certificate Wizard Line'
    
    period = fields.Char(string='Period')
    bank = fields.Char(string='Bank')
    branch = fields.Char(string='Branch/City')
    amount = fields.Float(string='Amount', digits=(12, 0))
    certificate_id = fields.Many2one('tax.certificate.wizard', string='Certificate')
    
