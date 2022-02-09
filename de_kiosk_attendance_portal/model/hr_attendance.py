# -*- coding: utf-8 -*-
from odoo import api, fields, models, _    

class HrAttendances(models.Model):
    _inherit = 'hr.attendance' 


class HrAttendanceWFH(models.Model):
    _name='hr.attendance.wfh'

  
    