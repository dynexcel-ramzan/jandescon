# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    
    remarks = fields.Char(string="Remarks", required=False)
   
 