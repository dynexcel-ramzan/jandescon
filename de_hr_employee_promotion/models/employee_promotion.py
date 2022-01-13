# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timezone,date

class EmployeePromotion(models.Model):
    _name = 'hr.employee.promotion'
    _description = 'employee promotion'
    _rec_name = 'employee_id'
    

    currency_id = fields.Many2one('res.currency', string="Currency")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    contract_id = fields.Many2one('hr.contract', string="Contract")
    previous_wage = fields.Monetary(string='Previous Wage')
    pre_job_id = fields.Many2one('hr.job', string="Previous ")
    description = fields.Char(string="Description")
    date = fields.Date(string="Date", required=True)
    promotion_type = fields.Char(string="Promotion Type")
    new_wage = fields.Monetary(string="New Salary")
    new_job_id = fields.Many2one('hr.job', string="New Designation")
    period = fields.Selection( 
        [
        ('01', 'Jan'),
        ('02', 'Feb'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'Jun'),
        ('07', 'July'),
        ('08', 'Aug'),
        ('09', 'Sep'),
        ('10', 'Oct'),
        ('11', 'Nov'),
        ('12', 'Dec'),    
         ],
         string='Period')
    tax_year = fields.Char(string='Tax Year')    
    old_department_id = fields.Many2one('hr.department', string='Old Department')
    new_department_id = fields.Many2one('hr.department', string='New Department')    
    loc_show_hide = fields.Boolean(string = "is Transfer?")
    old_location_id = fields.Many2one('hr.work.location', string='Old Work Location')
    new_location_id = fields.Many2one('hr.work.location', string='New Work Location')
    
    @api.onchange('date')
    def onchange_date(self):
        for line in self:
            if line.date:
                line.update({
                    'tax_year': line.date.strftime('%Y'),
                    'period': line.date.strftime('%m'),
                })
    
    @api.onchange('employee_id')
    def onchange_employee(self):
        for promotion in self:
            contract = self.env['hr.contract'].search([('employee_id','=',promotion.employee_id.id),('state','=','open')], limit=1)
            promotion.update({
                'contract_id': contract.id,
                'pre_job_id': promotion.employee_id.job_id.id,
                'previous_wage': contract.wage,
                'old_department_id': promotion.employee_id.department_id.id,
                'old_location_id': promotion.employee_id.work_location_id.id,
            })
            
            
            
            
    @api.model_create_multi
    def create(self, vals_list):
        rslt = super(EmployeePromotion, self).create(vals_list)
        rslt.action_update_contract_wage()
        return rslt        
        
    
    def action_update_contract_wage(self):
        for line in self:
            line.update({
                    'tax_year': line.date.strftime('%Y'),
                    'period': line.date.strftime('%m'),
                })
            line.contract_id.wage=line.new_wage
            if line.new_department_id:
                line.employee_id.update({
                    'department_id': line.new_department_id.id,
                })
            if line.new_job_id:
                line.employee_id.update({
                    'job_id': line.new_job_id.id,
                })    
            if line.new_location_id:
                line.employee_id.update({
                    'work_location_id': line.new_location_id.id,
                })
    
class HrEmployeeInherit(models.Model):
    _inherit = "hr.employee"
    
    promotion_ids = fields.One2many('hr.employee.promotion','employee_id')
    
    
    

