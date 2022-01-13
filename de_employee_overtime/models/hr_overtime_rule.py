# -*- coding: utf-8 -*-

from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.resource.models.resource import HOURS_PER_DAY




    
class HrOverTimeRule(models.Model):
    _name = 'hr.overtime.rule'
    _description = "HR Overtime Rule"
    _inherit = ['mail.thread']
    
    name = fields.Char(string="Name" )
    company_id = fields.Many2one('res.company', string="Company")
    rule_type = fields.Selection([('maximum', 'Maximum'),
                              ('minimum', 'Minimum'),
                              ], string="Rule Type",
                             default="maximum",  required=True, track_visibility=True)
    
    rule_period = fields.Selection([('day', 'Day'),
                              ('week', 'Week'),
                              ('month', 'Month'),
                              ], string="Period",
                             default="month" ,  required=True)
    hours = fields.Integer(string="Hours" ,  required=True)
    
    
    
    
    

 
    

    