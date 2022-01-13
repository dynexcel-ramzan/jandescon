# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    vehicle_meter_line_ids = fields.One2many('vehicle.meter.reading', 'employee_id', string='Vehicle Meter Line')
    medical_line_ids = fields.One2many('medical.reading', 'employee_id', string='Medical Line')
    vehicle_id = fields.Many2one('vehicle.meter.detail', string='Vehicle')
    expense_incharge_id = fields.Many2one('hr.employee', string='Expense Incharge')

class MedicalLine(models.Model):
    _name = 'medical.reading'
    _description= 'Medical Reading'
    
    sub_category_id = fields.Many2one('expense.sub.category', string='Type', required=True, domain="[('ora_unit','=', 'amount')]")
    limit = fields.Float(string='Limit')
    last_paid = fields.Float(string='Paid')
    ora_unit = fields.Selection(selection=[
            ('amount', 'Amount'),
            ('km', 'Km'),
        ], string='Unit', 
        )
    employee_id = fields.Many2one('hr.employee', string='Employee')
    
    @api.onchange('sub_category_id')
    def onchange_sub_category_id(self):
        for line in self:
            if line.sub_category_id:
                line.update({
                    'limit': line.sub_category_id.amount, 
                    'ora_unit': line.sub_category_id.ora_unit,
                })    
    
class VehicleMeterLine(models.Model):
    _name = 'vehicle.meter.reading'
    _description= 'Vehicle Meter Reading'
    
    sub_category_id = fields.Many2one('expense.sub.category', required=True, string='Type', domain="[('ora_unit','=', 'km')]")
    limit_reading = fields.Float(related='sub_category_id.meter_reading', string='Limit')
    opening_reading = fields.Integer(string='Last Reading')
    ora_unit = fields.Selection(related='sub_category_id.ora_unit', string='Unit')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    
    
    