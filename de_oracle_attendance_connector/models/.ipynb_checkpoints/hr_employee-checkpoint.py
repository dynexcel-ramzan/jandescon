# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    oralce_employee_no = fields.Char(string="EBS Employee No.")

    