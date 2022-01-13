# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime


class HrAttendance(models.Model):
    _name = 'hr.device.attendance'
    _description = 'Attendance Device'
    
    
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company',string='Company', required=True)
    device_id = fields.Integer(string='Device ID', required=True)
    mode = fields.Selection([('check_in', 'Check In'), 
                             ('check_out', 'Check Out'), 
                             ], default='check_in' , required=True)
    
    
    

