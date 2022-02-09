# -*- coding: utf-8 -*-

from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.resource.models.resource import HOURS_PER_DAY


class HrOverTimeType(models.Model):
    _name = 'hr.overtime.type'
    _description = "HR Overtime Type"
    _inherit = ['mail.thread']

    
    
    name = fields.Char(string="Name" , required=True)
    company_id = fields.Many2one('res.company', string="Company")
    type_line_ids = fields.One2many('hr.overtime.type.line', 'overtime_type_id' , string="Type Line")
    type = fields.Selection([('gazetted', 'Gazetted'),
                              ('normal', 'Normal'),
                              ('rest_day', 'Rest Day'),
                              ], string="Type",
                             default="normal", required=True)
    work_location_id = fields.Many2one('hr.work.location', string="Work Location", domain="[('company_id','=',company_id)]")

    
    
class HrOverTimeTypeLine(models.Model):
    _name = 'hr.overtime.type.line'
    _description = "HR Overtime Type Line"

    
    
    compansation = fields.Selection([('payroll', 'Payroll'),
                              ('leave', 'Leave'),
                              ], string="Compansation",
                             default="payroll", required=True)
    rate_type = fields.Selection([('fix_amount', 'Fix'),
                              ('percent', 'Percentage'),
                              ], string="Rate Type",
                             default="fix_amount")
    
    company_id = fields.Many2one(related='overtime_type_id.company_id')
    rate = fields.Float(string='Rate Per Hour', default=2)
    rate_percent = fields.Float(string='Rate', default=2)
    hours_per_day = fields.Integer(string='Hours', default=8)
    month_day = fields.Integer(string='Days', default=30)
    ot_hours = fields.Float(string='Min OT Hours')
    leave_type_id = fields.Many2one('hr.leave.type', string="Leave Type")
    leave_type = fields.Selection([('half_day', 'Half Day'),
                              ('full_day', 'Full Day'),
                              ], string="Leave Period",
                             default="half_day")
    overtime_type_id = fields.Many2one('hr.overtime.type', string="Overtime Type")
    
    entry_type_id = fields.Selection([('double', 'Split'),
                              ('single', 'Normal'),
                              ], string="Compansation Type",
                             default="single")
    
    
