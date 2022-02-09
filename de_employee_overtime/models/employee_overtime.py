from odoo import models, fields, api, _
from datetime import datetime
from odoo import exceptions 
from odoo.exceptions import UserError, ValidationError 





class HrEmployee(models.Model):
    _inherit = 'hr.employee'
     
    allow_overtime = fields.Boolean(string='OT Allowed', )

    
    

class EmployeeOvertime(models.Model):
    _name = 'hr.employee.overtime'
    _description = 'Employee Overtime'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'employee_id'
    
    def unlink(self):
        for leave in self:
            if leave.state in ('to_approve','approved','paid'):
                raise UserError(_('You cannot delete an order form  which is not draft or close. '))
     
            return super(EmployeeOvertime, self).unlink()
        
    def action_approve(self):
                     
        self.write ({
                'state': 'approved'
                    })
        
    def action_confirm(self):
        self.write ({
                'state': 'to_approve'
            })    
        
    def action_refuse(self):
        self.write ({
                'state': 'refused'
            })
        
    def action_draft(self):
        self.write ({
                'state': 'draft'
            })    
    
    employee_id = fields.Many2one('hr.employee', string="Employee", store=True)
    overtime_type_id = fields.Many2one('hr.overtime.type', string="Overtime Type", store=True)
    date = fields.Date(string='Date', required=True)
    check_in = fields.Datetime(string="Check In", readonly=True)
    check_out = fields.Datetime(string="Check Out", readonly=True)
    total_hours = fields.Float(string="Total Hours", readonly=True)
    overtime_hours = fields.Float(string="Overtime Hours", readonly=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('to_approve', 'To Approve'),
        ('refused', 'Refused'),
        ('approved', 'Approved'),        
        ('paid', 'Paid'),
        ('close', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    

    
class OvertimeType(models.Model):
    _name = 'overtime.type'
    
    
class OvertimeType(models.Model):
    _name = 'hr.overtime'  

class OvertimeType(models.Model):
    _name = 'hr.overtime.type.rule'    