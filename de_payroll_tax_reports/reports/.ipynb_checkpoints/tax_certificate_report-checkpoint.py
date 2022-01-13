# -*- coding: utf-8 -*-
#################################################################################
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-today Dynexcel <www.dynexcel.com>

#################################################################################
import time
from odoo import api, models, fields, _
from dateutil.parser import parse
from odoo.exceptions import UserError

class PayrollTaxComputation(models.AbstractModel):
    _name = 'report.de_payroll_tax_reports.certificate_report'
    _description = 'Tax certificate Report'

    '''Find payroll Tax certificate Report between the date'''
    @api.model
    def _get_report_values(self, docids, data=None): 
        docs = self.env['tax.certificate.wizard'].browse(self.env.context.get('active_id'))
        certificate_list = []
        for line in docs.certificate_line_ids:
            certificate_list.append({
                'period': line.period,
                'bank': line.bank,
                'branch': line.branch,
                'amount': line.amount,
            })    
        return {
                'docs': docs,
                'issue_date': fields.date.today(),
                'certificate_list': certificate_list,
            }
       