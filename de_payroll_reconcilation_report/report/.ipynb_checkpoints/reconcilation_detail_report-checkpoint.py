# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2019-today Business Solution <www.dynexcel.com>

#################################################################################
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


class ReconcilationDetailReport(models.AbstractModel):
    _name = 'report.de_payroll_reconcilation_report.detail_report'
    _description = 'Reconciliation Detail Report'

    
    
    '''Find payroll reconcilation detail report between the date'''
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['reconciliation.detail.wizard'].browse(self.env.context.get('active_id'))          
        return {
            'docs': docs,
        }