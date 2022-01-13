# -*- coding: utf-8 -*-
from odoo.exceptions import Warning
from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    shift_id = fields.Many2one('resource.calendar', string="Active Shift", help="Shift schedule")
    


    