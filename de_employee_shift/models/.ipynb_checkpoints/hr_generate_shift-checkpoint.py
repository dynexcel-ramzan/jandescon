# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class HrGenerateShift(models.Model):
    _name = 'hr.shift.generate'
    _rec_name='start_date'

    hr_department = fields.Many2many('hr.department', string="Department", help="Department")
    start_date = fields.Date(string="Start Date", required=True, help="Start date")
    end_date = fields.Date(string="End Date", required=True, help="End date")
    company_id = fields.Many2one('res.company', string='Company', help="Company", default=lambda self: self.env.company )
    employee_ids = fields.Many2many('hr.employee', string="Employees")
    employee_category_ids = fields.Many2many('hr.employee.category', string="Employee Category")
    shift_id = fields.Many2many('resource.calendar',string="Shifts", required=True, domain="['|',('company_id','=',company_id),('company_id','=',False)]")
    week_day_ids = fields.Many2many('shift.week.days', string='Rest Days')
    schedule_line_ids = fields.One2many('hr.shift.schedule.generate.line', 'wizard_generate_id',string="Shedule")
    
    
    
    @api.onchange('start_date','end_date','shift_id')
    def onchange_shift(self):
        if self.start_date and self.end_date and self.shift_id:
             
            for line in self.schedule_line_ids:            
                line.unlink()
            if self.start_date and self.end_date:
                delta = self.start_date - self.end_date
                total_days = abs(delta.days)
                for i in range(0, total_days + 1):
                    date_after_month = self.start_date + relativedelta(days=i)
                    day_week = '0'
                    shift_one_type = 0
                    shift_two_type = 0
                    shift_one = 0
                    shift_two = 0
                    rest_day = False
                    if date_after_month.weekday() == 0:
                        day_week = self.env['shift.week.days'].search([('name','=','Monday')], limit=1)
                        for day in self.week_day_ids:
                            if day.name == 'Monday':
                                
                                rest_day = True

                        count1 = 0       
                        for shift in self.shift_id: 
                            if count1 == 0:
                                shift_one_type_str = str(shift.id)
                                shift_one_type1 = shift_one_type_str.split('NewId_')
                                shift_id = ' '
                                for final_shift in shift_one_type1:
                                    shift_id = shift_id + final_shift


                                shift_one_type = int(shift_id)
                                shift_resourcem1 = self.env['resource.calendar'].search([('id','=',shift_one_type)], limit=1)
                                shift_one = shift_resourcem1.id
                                count1 = count1 + 1
                            elif count1 == 1:
                                shift_two_type_str = str(shift.id)
                                shift_two_type1 = shift_two_type_str.split('NewId_')
                                shift_id2 = ' '
                                for final_shift in shift_two_type1:
                                    shift_id2 = shift_id2 + final_shift                                
                                shift_two_type = int(shift_id2)
                                shift_resourcem2 = self.env['resource.calendar'].search([('id','=',shift_two_type)], limit=1)
                                shift_two = shift_resourcem2.id
                                count1 = count1 + 1

                    elif date_after_month.weekday() == 1:
                        day_week = self.env['shift.week.days'].search([('name','=','Tuesday')], limit=1)
                        for day in self.week_day_ids:
                            if day.name == 'Tuesday':
                                rest_day = True 

                        count1 = 0       
                        for shift in self.shift_id: 
                            if count1 == 0:
                                shift_one_type_str = str(shift.id)
                                shift_one_type1 = shift_one_type_str.split('NewId_')
                                shift_id = ' '
                                for final_shift in shift_one_type1:
                                    shift_id = shift_id + final_shift

                                shift_one_type = int(shift_id) 
                                shift_resourcet1 = self.env['resource.calendar'].search([('id','=',shift_one_type)], limit=1)
                                shift_one = shift_resourcet1.id
                                count1 = count1 + 1
                            elif count1 == 1:
                                shift_two_type_str = str(shift.id)
                                shift_two_type1 = shift_two_type_str.split('NewId_')
                                shift_id2 = ' '
                                for final_shift in shift_two_type1:
                                    shift_id2 = shift_id2 + final_shift                                
                                shift_two_type = int(shift_id2) 
                                shift_resourcet2 = self.env['resource.calendar'].search([('id','=',shift_two_type)], limit=1)
                                shift_two = shift_resourcet2.id
                                count1 = count1 + 1        

                    elif date_after_month.weekday() == 2:
                        day_week = self.env['shift.week.days'].search([('name','=','Wednesday')], limit=1)
                        for day in self.week_day_ids:
                            if day.name == 'Wednesday':
                                rest_day = True 
                        count1 = 0       
                        for shift in self.shift_id: 
                            if count1 == 0:
                                shift_one_type_str = str(shift.id)
                                shift_one_type1 = shift_one_type_str.split('NewId_')
                                shift_id = ' '
                                for final_shift in shift_one_type1:
                                    shift_id = shift_id + final_shift


                                shift_one_type = int(shift_id) 
                                shift_resourcew1 = self.env['resource.calendar'].search([('id','=',shift_one_type)], limit=1)

                                shift_one = shift_resourcew1.id
                                count1 = count1 + 1
                            elif count1 == 1:
                                shift_two_type_str = str(shift.id)
                                shift_two_type1 = shift_two_type_str.split('NewId_')
                                shift_id2 = ' '
                                for final_shift in shift_two_type1:
                                    shift_id2 = shift_id2 + final_shift                                
                                shift_two_type = int(shift_id2)   
                                shift_resourcew2 = self.env['resource.calendar'].search([('id','=',shift_two_type)], limit=1)

                                shift_two = shift_resourcew2.id
                                count1 = count1 + 1        

                    elif date_after_month.weekday() == 3:
                        day_week = self.env['shift.week.days'].search([('name','=','Thursday')], limit=1)
                        for day in self.week_day_ids:
                            if day.name == 'Thursday':
                                rest_day = True 
                        count1 = 0       
                        for shift in self.shift_id: 
                            if count1 == 0:
                                shift_one_type_str = str(shift.id)
                                shift_one_type1 = shift_one_type_str.split('NewId_')
                                shift_id = ' '
                                for final_shift in shift_one_type1:
                                    shift_id = shift_id + final_shift

                                shift_one_type = int(shift_id)
                                shift_resourceth1 = self.env['resource.calendar'].search([('id','=',shift_one_type)], limit=1)

                                shift_one = shift_resourceth1.id                        
                                count1 = count1 + 1
                            elif count1 == 1:
                                shift_two_type_str = str(shift.id)
                                shift_two_type1 = shift_two_type_str.split('NewId_')
                                shift_id2 = ' '
                                for final_shift in shift_two_type1:
                                    shift_id2 = shift_id2 + final_shift                                
                                shift_two_type = int(shift_id2)   
                                shift_resourceth2 = self.env['resource.calendar'].search([('id','=',shift_two_type)], limit=1)

                                shift_two = shift_resourceth2.id
                                count1 = count1 + 1        

                    elif date_after_month.weekday() == 4:
                        day_week = self.env['shift.week.days'].search([('name','=','Friday')], limit=1)
                        for day in self.week_day_ids:
                            if day.name == 'Friday':
                                rest_day = True 
                        count1 = 0       
                        for shift in self.shift_id: 
                            if count1 == 0:
                                shift_one_type_str = str(shift.id)
                                shift_one_type1 = shift_one_type_str.split('NewId_')
                                shift_id = ' '
                                for final_shift in shift_one_type1:
                                    shift_id = shift_id + final_shift

                                shift_one_type = int(shift_id) 
                                shift_resourcef1 = self.env['resource.calendar'].search([('id','=',shift_one_type)], limit=1)

                                shift_one = shift_resourcef1.id
                                count1 = count1 + 1
                            elif count1 == 1:
                                shift_two_type_str = str(shift.id)
                                shift_two_type1 = shift_two_type_str.split('NewId_')
                                shift_id2 = ' '
                                for final_shift in shift_two_type1:
                                    shift_id2 = shift_id2 + final_shift                                
                                shift_two_type = int(shift_id2)
                                shift_resourcef2 = self.env['resource.calendar'].search([('id','=',shift_two_type)], limit=1)
                                shift_two = shift_resourcef2.id
                                count1 = count1 + 1        

                    elif date_after_month.weekday() == 5:
                        day_week = self.env['shift.week.days'].search([('name','=','Saturday')], limit=1)
                        for day in self.week_day_ids:
                            if day.name == 'Saturday':
                                rest_day = True 
                        count1 = 0       
                        for shift in self.shift_id: 
                            if count1 == 0:
                                shift_one_type_str = str(shift.id)
                                shift_one_type1 = shift_one_type_str.split('NewId_')
                                shift_id = ' '
                                for final_shift in shift_one_type1:
                                    shift_id = shift_id + final_shift

                                shift_one_type = int(shift_id)
                                shift_resourcesa1 = self.env['resource.calendar'].search([('id','=',shift_one_type)], limit=1)
                                shift_one = shift_resourcesa1.id
                                count1 = count1 + 1
                            elif count1 == 1:
                                shift_two_type_str = str(shift.id)
                                shift_two_type1 = shift_two_type_str.split('NewId_')
                                shift_id2 = ' '
                                for final_shift in shift_two_type1:
                                    shift_id2 = shift_id2 + final_shift                                
                                shift_two_type = int(shift_id2) 
                                shift_resourcesa2 = self.env['resource.calendar'].search([('id','=',shift_two_type)], limit=1)
                                shift_two = shift_resourcesa2.id
                                count1 = count1 + 1        

                    elif date_after_month.weekday() == 6:
                        day_week = self.env['shift.week.days'].search([('name','=','Sunday')], limit=1)
                        for day in self.week_day_ids:
                            if day.name == 'Sunday':
                                rest_day = True 

                        count1 = 0       
                        for shift in self.shift_id: 
                            if count1 == 0:
                                shift_one_type_str = str(shift.id)
                                shift_one_type1 = shift_one_type_str.split('NewId_')
                                shift_id = ' '
                                for final_shift in shift_one_type1:
                                    shift_id = shift_id + final_shift

                                shift_one_type = int(shift_id) 
                                shift_resources1 = self.env['resource.calendar'].search([('id','=',shift_one_type)], limit=1)
                                shift_one = shift_resources1.id
                                count1 = count1 + 1
                            elif count1 == 1:
                                shift_two_type_str = str(shift.id)
                                shift_two_type1 = shift_two_type_str.split('NewId_')
                                shift_id2 = ' '
                                for final_shift in shift_two_type1:
                                    shift_id2 = shift_id2 + final_shift                                
                                shift_two_type = int(shift_id2)
                                shift_resources2 = self.env['resource.calendar'].search([('id','=',shift_two_type)], limit=1)
                                shift_two = shift_resources2.id
                                count1 = count1 + 1        

                    if rest_day == True:
                        vals = {
                            'wizard_generate_id': self.id,
                            'date': date_after_month,
                            'day': day_week.id,
                            'first_shift_id':False,
                            'second_shift_id': False,
                            'rest_day': rest_day
                        }
                        self.env['hr.shift.schedule.generate.line'].create(vals)
                    else:
                        vals = {
                            'wizard_generate_id': self.id,
                            'date': date_after_month,
                            'day': day_week.id,
                            'first_shift_id':shift_one,
                            'second_shift_id': shift_two,
                            'rest_day': rest_day
                        }
                        self.env['hr.shift.schedule.generate.line'].create(vals)






    
    
    def action_schedule_shift(self):
        """Create mass schedule for all departments based on the shift scheduled in corresponding employee's contract"""
        
        if self.employee_ids:
            for employee in self.employee_ids:  
                vals = {
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'employee_id':employee.id,
                    'company_id': employee.company_id.id,
                }
                shift_schedule = self.env['hr.shift.schedule'].create(vals)
                for line in self.schedule_line_ids:                    
                    line_vals = {
                        'generate_id': shift_schedule.id,
                        'employee_id': employee.id,
                        'day': line.day.id,
                        'date': line.date,
                        'first_shift_id': line.first_shift_id.id,
                        'second_shift_id':line.second_shift_id.id,
                        'rest_day': line.rest_day, 
                    }
                    shift_schedule_line = self.env['hr.shift.schedule.line'].create(line_vals)
                shift_schedule.action_post()
                
        elif  self.employee_category_ids:
            for employee_categ in self.employee_category_ids:  
                employee_contract1 = self.env['hr.employee'].search([('category_ids', '=', employee_categ.id),], limit=1)
                
                for employee in employee_contract1:  
                    vals = {
                        'start_date': self.start_date,
                        'end_date': self.end_date,
                        'state': 'posted',
                        'employee_id':employee.id,
                        'company_id': employee.company_id.id,
                    }
                    shift_schedule = self.env['hr.shift.schedule'].create(vals)
                    for line in self.schedule_line_ids:

                        line_vals = {
                            'generate_id': shift_schedule.id,
                            'day': line.day.id,
                            'date': line.date,
                            'first_shift_id': line.first_shift_id.id,
                            'second_shift_id':line.second_shift_id.id,
                            'rest_day': line.rest_day, 
                        }
                        shift_schedule_line = self.env['hr.shift.schedule.line'].create(line_vals)
                    shift_schedule.action_post()



        elif self.hr_department:
            for dept in self.hr_department:
                employees = self.env['hr.employee'].search([('department_id', '=', dept.id)]) 
                for employee in employees:
                    vals = {
                        'start_date': self.start_date,
                        'end_date': self.end_date,
                        'state': 'posted',
                        'employee_id':employee.id,
                        'company_id': employee.company_id.id,
                    }
                    shift_schedule = self.env['hr.shift.schedule'].create(vals)
                    for line in self.schedule_line_ids:

                        line_vals = {
                            'generate_id': shift_schedule.id,
                            'day': line.day.id,
                            'date': line.date,
                            'first_shift_id': line.first_shift_id.id,
                            'second_shift_id':line.second_shift_id.id,
                            'rest_day': line.rest_day, 
                        }
                        shift_schedule_line = self.env['hr.shift.schedule.line'].create(line_vals)
                    shift_schedule.action_post()



                        
                        
                        
    
class HrScheduleLine(models.Model):
    _name = 'hr.shift.schedule.generate.line'

    wizard_generate_id = fields.Many2one('hr.shift.generate', string='Generate', help="Generate")
    company_id = fields.Many2one(related='wizard_generate_id.company_id')
    date = fields.Date(string="Date", required=True, help="Starting date for the shift") 
    day = fields.Many2one('shift.week.days', string='Day')
    first_shift_id = fields.Many2one('resource.calendar', string="First Shift", required=False, help="Shift", domain="['|',('company_id','=',company_id),('company_id','=',False)]")
    second_shift_id = fields.Many2one('resource.calendar', string="Second Shift", required=False, help="Shift", domain="['|',('company_id','=',company_id),('company_id','=',False)]")
    rest_day = fields.Boolean(string="Rest Day")
   
    
 
                              

class RestDayLine(models.Model):
    _name = 'hr.rest.day.generate.line'
    _description = 'Rest Days'
    


    date = fields.Date(string='Date')
    contract_id = fields.Many2one('hr.shift.generate', string='Shift')
   