# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timezone,date

class EmployeePromotion(models.Model):
    
    _name = 'hr.employee.promotion'
    _description = 'this table is relevent to employee promotion'
    _rec_name = 'employee_id'
    

    currency_id = fields.Many2one('res.currency', string="Currency")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    contract_id = fields.Many2one('hr.contract', string="Contract")
    previous_salary = fields.Monetary(related='contract_id.wage')
    previous_designation = fields.Many2one('hr.job', string="Previous Designation")
    description = fields.Char(string="Description")
    date = fields.Date(string="Date")
    promotion_type = fields.Char(string="Promotion Type")
    new_salary = fields.Char(string="New Salary")
    new_designation = fields.Many2one('hr.job', string="New Designation")
    
    
    old_department = fields.Many2one('hr.department', string='Old Department')
    new_department = fields.Many2one('hr.department', string='New Department')
    
    loc_show_hide = fields.Boolean(string = "is Transfer?")
    old_location = fields.Many2one('res.city', string='Old Location')
    new_location = fields.Many2one('res.city', string='New Location')
    
    
    
class HrEmployeeInherit(models.Model):
    _inherit = "hr.employee"
    
    promotion_ids = fields.One2many('hr.employee.promotion','employee_id')
    
    
    

class EmployeePromotion(models.Model):
    _name = 'res.city'
    _description = 'this table is relevent to employee city'
    _rec_name = 'city'
    
    country = fields.Char(string="Country")
    city = fields.Char(string="City")
    zip = fields.Char(string="Zip")