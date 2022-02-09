# -*- coding: utf-8 -*-
from odoo.exceptions import Warning, UserError
from odoo import models, fields, api, _




class HrSchedule(models.Model):
    _name = 'hr.shift.schedule'
    _rec_name = 'employee_id'

    start_date = fields.Date(string="Date From", required=True, help="Starting date for the shift", readonly=True)
    end_date = fields.Date(string="Date To", required=True, help="Ending date for the shift", readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", readonly=True)
    employee_number = fields.Char(string='Employee Number', compute='_compute_emp_number', store=True)	
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')
    department_id = fields.Many2one(related='employee_id.department_id')
    dept_id = fields.Many2one('hr.department', string="Department")
    company_id = fields.Many2one('res.company', string="Company", help="Company", readonly=True)
    schedule_line_ids = fields.One2many('hr.shift.schedule.line', 'generate_id' , string="Shedule", required=False, help="Schedule")

    @api.depends('employee_id')
    def _compute_emp_number(self):
        for shift in self:
            shift.update({
               'employee_number':  shift.employee_id.emp_number
                 })   
    
    def action_cancel(self):
        for shift in self:
            shift.update({
                'state': 'cancel'
            })
            for shift_line in shift.schedule_line_ids:
                shift_line.update({
                'state': 'cancel'
                })    
   
    def action_post(self):
        for shift in self:
            shift.update({
                'state': 'posted'
            })
            for shift_line in shift.schedule_line_ids:
                shift_line.update({
                'state': 'posted'
                })   
                
                
    def action_draft(self):
        for shift in self:
            shift.update({
                'state': 'draft'
            })
            for shift_line in shift.schedule_line_ids:
                shift_line.update({
                'state': 'draft'
                })
                
            
    def unlink(self):
        for shift in self:
            if shift.state == 'posted':
                raise UserError(_("You cannot delete an entry which not in cancel or draft."))
        self.schedule_line_ids.unlink()
        return super(HrSchedule, self).unlink()        
    
    @api.onchange('department_id')
    def onchange_department(self):
        if self.department_id:
            self.dept_id = self.department_id    
        
    

    
    def write(self, vals):
        self._check_overlap(vals)
        return super(HrSchedule, self).write(vals)

    @api.model
    def create(self, vals):
        self._check_overlap(vals)
        return super(HrSchedule, self).create(vals)

    def _check_overlap(self, vals):
        if vals.get('start_date', False) and vals.get('end_date', False):
            shifts = self.env['hr.shift.schedule'].search([('employee_id', '=', vals.get('employee_id'))])
            for each in shifts:
                if each != shifts[-1]:
                    if str(each.end_date ) >= str(vals.get('start_date')) or str(each.start_date) >= str(vals.get('start_date')):
                        raise Warning(_('The dates may not overlap with one another.'))
            if str(vals.get('start_date')) > str(vals.get('end_date')):
                raise Warning(_('Start date should be less than end date.'))
        return True
    
 

                    
class HrScheduleLine(models.Model):
    _name = 'hr.shift.schedule.line'

    date = fields.Date(string="Date", required=True, help="Starting date for the shift") 
    day = fields.Many2one('shift.week.days', string='Day')
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ], string='Status', required=True, readonly=False, copy=False, tracking=True,
        default='draft')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    employee_number = fields.Char(string='Employee Number', compute='_compute_emp_number', store=True) 
    first_shift_id = fields.Many2one('resource.calendar', string="First Shift", required=False, help="Shift", domain="['|',('company_id','=',company_id),('company_id','=',False)]")
    second_shift_id = fields.Many2one('resource.calendar', string="Second Shift", required=False, help="Shift", domain="['|',('company_id','=',company_id),('company_id','=',False)]")
    rest_day = fields.Boolean(string="Rest Day")
    generate_id = fields.Many2one('hr.shift.schedule', string='Generate', help="Generate")
    company_id = fields.Many2one(related='generate_id.company_id')

    @api.depends('employee_id')
    def _compute_emp_number(self):
        for shift in self:
            shift.update({
               'employee_number':  shift.employee_id.emp_number
                 }) 
    
   
    

  

class ShiftWeekdays(models.Model):
    _name = 'shift.week.days'
    _description = 'This table handle the data of shift allocation weekdays'
    
    name = fields.Char(string="Day")    
   
        