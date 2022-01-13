# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime
import base64

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips, ResultRules
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval

class HrLoanProof(models.Model):
    _name = 'hr.loan.proof'
    _description = 'This Is Loan Proof'
    _inherit = ['portal.mixin', 'mail.thread']
    
    name = fields.Char(string="Name", required=True)
    mandatory = fields.Boolean(string="Mandatory")

   