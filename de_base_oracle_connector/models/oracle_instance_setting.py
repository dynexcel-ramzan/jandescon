# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
from odoo.exceptions import ValidationError
import cx_Oracle

logger = logging.getLogger(__name__)



class OracleInstanceSetting(models.Model):
    _name = 'oracle.instance.setting'
    _description = 'Oracle Database Instance'
    _order = "name desc"

    name = fields.Char(string='Instance Name', required=True)
    host = fields.Char(string="Host", required=True)
    port = fields.Char(string="Port", required=True)
    user = fields.Char(string="User Name", required=True)
    password = fields.Char(string="Password", required=True)
    db_name = fields.Char(string="Oracle Database", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('close', 'Close')],
        readonly=False, string='State', index=True , default='draft')

    def action_active(self):
        self.write({
            'state': 'active'
        })

    def try_connection(self):
        try:
            tusername = self.user
            tpasswrd = self.password
            thost = self.host
            tport = self.port
            tinstance = self.db_name
            conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
            cur = conn.cursor()
            if conn:
                self.write({
                    'state': 'active'
                })
            if conn:
                raise ValidationError('Successfully Connected')



        except Exception as e:
            raise ValidationError(e)

    def action_send_data(self):
        invoices = self.env['account.move.line'].search([])
        for inv in invoices:
            inv_name = inv.name
            ledger_id = inv.move_id.company_id.ledger_id
            currency_code = inv.company_id.currency_id.name
            date_created = fields.date.today()
            created_by = -1
            flag = 'A'
            segment1 = inv.move_id.company_id.segment1
            segment2 = 502
            segment3 = 7512
            segment4 = 5102
            segment5 =  0
            segment6 =  0
            entered_dr = inv.debit
            entered_cr = inv.credit
            accounting_dr = inv.debit
            accountng_cr = inv.credit
            ref1 = str(inv.id) + ' ' + 'odoo' +  ' ' + 'payroll'  
            reference1 = ref1
            ref2 = 'journal import odoo' + ' '+ 'odoo' + ' ' + 'payroll'
            reference2 = ref2
            ref4 = 'JV'+ ' '+ 'March-21'+ ' '+ 'odoo'+ ' ' + 'payroll' +  str(inv.move_id.journal_id.name)
            reference4 = ref4
            ref5 = 'journal import odoo' + ' '+ 'odoo' + ' ' + 'payroll'
            reference5 = ref5
            reference6 = inv.id
            emp_office_id = 24
            employee_office_id = self.env['hr.employee'].search([('address_home_id','=', inv.partner_id.id)])
            for emp in employee_office_id:
                emp_office_id = emp.emp_number    
            ref10 = str(inv.name) + ' ' + str(inv.partner_id.name) + ' ' + str(emp_office_id)
            reference10 = ref10
            group_id = inv.move_id.id
            period_name = inv.move_id.ref
            context = inv.analytic_account_id.name
            attribute1 = inv.analytic_account_id.code
            inv_debit = inv.debit
            inv_credit = inv.credit
            inv_date = inv.date
            tusername = self.user
            tpasswrd = self.password
            thost = self.host
            tport = self.port
            tinstance = self.db_name
            conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
            cur = conn.cursor()
            statement = 'insert into XX_ODOO_GL_INTERFACE(STATUS,LEDGER_ID, ACCOUNTING_DATE, CURRENCY_CODE,DATE_CREATED,CREATED_BY,ACTUAL_FLAG,USER_JE_CATEGORY_NAME,USER_JE_SOURCE_NAME, SEGMENT1, SEGMENT2, SEGMENT3, SEGMENT4, SEGMENT5, SEGMENT6, ENTERED_CR, ENTERED_DR, ACCOUNTED_CR, ACCOUNTED_DR, REFERENCE1, REFERENCE2, REFERENCE4, REFERENCE5, REFERENCE6, REFERENCE10, GROUP_ID, PERIOD_NAME, CONTEXT, ATTRIBUTE1) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,: 14,:15,: 16,:17,: 18,:19,: 20,:21,: 22,:23,: 24,:25,: 26,:27,:28,:29,:30)'
            cur.execute(statement, (
            'NEW', ledger_id, inv_date, currency_code, date_created, created_by, flag, 'odoo', 'payroll',
            segment1, segment2, segment3, segment4, segment5,segment6, entered_cr, entered_dr, accountng_cr, accounting_dr,
            reference1, reference2,
            reference4, reference5, reference6, reference10, group_id, period_name,context,attribute1))
            conn.commit()









