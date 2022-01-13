# -*- coding: utf-8 -*-

from dateutil import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.resource.models.resource import HOURS_PER_DAY


class HrOverTimeEntry(models.Model):
    _name = 'hr.overtime.entry'
    _description = "HR Overtime Entry"
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    
       
    employee_id = fields.Many2one('hr.employee', string="Name")
    date = fields.Date('Date')
    amount = fields.Float('Overtime Amount',  store=True)
    company_id = fields.Many2one('res.company', string="Company")
    overtime_type_id = fields.Many2one('hr.overtime.type', string="Overtime Type")
    overtime_hours = fields.Float(string="Overtime Hours")
    remarks = fields.Char(string="Remarks")
