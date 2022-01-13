# -*- coding: utf-8 -*-

from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.resource.models.resource import HOURS_PER_DAY


class HrWorkLocation(models.Model):
    _name = 'hr.work.location'
    _description = "HR Work Location"
    _inherit = ['mail.thread']

    
    
    name = fields.Char(string="Name" , required=True)
    company_id = fields.Many2one('res.company', string="Company", required=True)