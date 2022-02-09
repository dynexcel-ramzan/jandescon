# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import cx_Oracle
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta

class ResCompany(models.Model):
    _inherit = 'res.company'

    hr_id = fields.Many2one('hr.employee', string='HR')