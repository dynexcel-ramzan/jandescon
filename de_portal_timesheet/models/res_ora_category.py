# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
# import cx_Oracle
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class ResORAClient(models.Model):
    _name = 'res.ora.category'
    _description= 'Res ORA Category'

    
    name = fields.Char(string='Description')
    code = fields.Char(string='Code')

