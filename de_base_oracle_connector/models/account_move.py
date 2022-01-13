# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
from odoo.exceptions import ValidationError
import cx_Oracle

logger = logging.getLogger(__name__)




class AccountAccount(models.Model):
    _inherit = 'account.move'

    is_posted = fields.Boolean(string="Posted On Oracle")
    
    
    def action_posted_on_oracle(self):
        for inv in self.line_ids:
            inv_name = inv.name
            ledger_id = inv.move_id.company_id.ledger_id
            currency_code = inv.company_id.currency_id.name
            date_created = fields.date.today()
            created_by = -1
            flag = 'A'
            journal = inv.move_id.journal_id.name
            segment1 = inv.move_id.company_id.segment1
            segment2 = inv.account_id.segment2
            segment3 = inv.account_id.segment3
            segment4 = inv.account_id.segment4
            segment5 =  inv.account_id.segment5
            segment6 =  inv.account_id.segment6
            entered_dr = inv.debit
            entered_cr = inv.credit
            accounting_dr = inv.debit
            accountng_cr = inv.credit
            ref1 = str(inv.id) + ' ' + 'Odoo' +  ' ' +  str(inv.move_id.journal_id.name)  
            reference1 = ref1
            ref2 = 'Journal Import Odoo' + ' '+  str(inv.move_id.journal_id.name)
            reference2 = ref2
            ref4 = 'JV'+ ' '+ 'March-21'+ ' '+ 'Odoo'+ ' '  +  str(inv.move_id.journal_id.name)+ ' '  +  str(inv.move_id.name)
            reference4 = ref4
            ref5 = 'Journal Import' + ' ' + 'Odoo' + ' ' + ' '  +  str(inv.move_id.journal_id.name)
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
            context = inv.analytic_account_id.name if inv.analytic_account_id.name else 'NULL'
            attribute1 = inv.analytic_account_id.code if inv.analytic_account_id.code else 'NULL'
            inv_debit = inv.debit
            inv_credit = inv.credit
            inv_date = inv.date
            conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.7.153:1524/test3')
            cur = conn.cursor()
            statement = 'insert into XX_ODOO_GL_INTERFACE(STATUS,LEDGER_ID, ACCOUNTING_DATE, CURRENCY_CODE,DATE_CREATED,CREATED_BY,ACTUAL_FLAG,USER_JE_CATEGORY_NAME,USER_JE_SOURCE_NAME, SEGMENT1, SEGMENT2, SEGMENT3, SEGMENT4, SEGMENT5, SEGMENT6, ENTERED_CR, ENTERED_DR, ACCOUNTED_CR, ACCOUNTED_DR, REFERENCE1, REFERENCE2, REFERENCE4, REFERENCE5, REFERENCE6, REFERENCE10, GROUP_ID, PERIOD_NAME, CONTEXT, ATTRIBUTE1) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,: 14,:15,: 16,:17,: 18,:19,: 20,:21,: 22,:23,: 24,:25,: 26,:27,:28,:29,:30)'
            cur.execute(statement, (
            'NEW', ledger_id, inv_date, currency_code, date_created, created_by, flag, 'Odoo', journal,
            segment1, segment2, segment3, segment4, segment5,segment6, entered_cr, entered_dr, accountng_cr, accounting_dr,
            reference1, reference2,
            reference4, reference5, reference6, reference10, group_id, period_name,context,attribute1))
            conn.commit()
        self.is_posted = True             
    

















