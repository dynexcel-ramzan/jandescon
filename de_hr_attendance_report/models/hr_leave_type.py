# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class de_hr_attendance_report(models.Model):
    _inherit = 'hr.leave.type'
    
    is_rest_day = fields.Boolean(string='Rest Day')
