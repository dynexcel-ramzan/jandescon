import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api, _
from datetime import datetime
from odoo import exceptions 
from odoo.exceptions import UserError, ValidationError 
import math
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class HrOvertimeAllocate(models.TransientModel):
    _name = 'hr.overtime.allocate'
    _description = 'Hr Overtime Allocate Wizard'

    date_start = fields.Date(string='Date From')
    date_end = fields.Date(string='Date To')
    

    
    
    def get_normal_overtime_type(self, employee_company, work_location):
        """
         In this method you can get Normal Overtime 
         1- Work Location Wise.
         2- Compnay Wise 
         3- Universal 
        """
        overtime_type = self.env['hr.overtime.type'].search([('type','=','normal')], limit=1)
        if employee_company:
            overtime_type = self.env['hr.overtime.type'].search([('type','=','normal'),('company_id','=',employee_company)], limit=1)
            if not overtime_type:
                overtime_type = self.env['hr.overtime.type'].search([('type','=','normal')], limit=1)
            if work_location:
                overtime_type = self.env['hr.overtime.type'].search([('type','=','normal'),('company_id','=',employee_company),('work_location_id','=',work_location)], limit=1)
                if not overtime_type:
                    if employee_company:
                        overtime_type = self.env['hr.overtime.type'].search([('type','=','normal'),('company_id','=',employee_company)], limit=1)
                        if not overtime_type:
                            overtime_type = self.env['hr.overtime.type'].search([('type','=','normal')], limit=1)
                        
        return overtime_type
    
    
    
    def get_gazetted_overtime_type(self, employee_company, work_location):
        """
         In this method you can get Gazetted Overtime 
         1- Work Location Wise.
         2- Compnay Wise 
         3- Universal 
        """
        overtime_type = self.env['hr.overtime.type'].search([('type','=','gazetted')], limit=1) 
        if employee_company:
            overtime_type = self.env['hr.overtime.type'].search([('type','=','gazetted'),('company_id','=',employee_company)], limit=1)
            if not overtime_type:
                overtime_type = self.env['hr.overtime.type'].search([('type','=','gazetted')], limit=1) 

                if work_location: 
                    overtime_type = self.env['hr.overtime.type'].search([('type','=','gazetted'),('company_id','=',employee_company),('work_location_id','=',work_location)], limit=1)
                    if not overtime_type:
                        if employee_company:
                            overtime_type = self.env['hr.overtime.type'].search([('type','=','gazetted'),('company_id','=',employee_company)], limit=1)
                            if not overtime_type:
                                overtime_type = self.env['hr.overtime.type'].search([('type','=','gazetted')], limit=1)    

                        
        return overtime_type
    
    
    
        
    def get_rest_days_overtime_type(self, employee_company, work_location):
        """
         In this method you can get Rest Day Overtime 
         1- Work Location Wise.
         2- Compnay Wise 
         3- Universal 
        """
        overtime_type = self.env['hr.overtime.type'].search([('type','=','rest_day')], limit=1)
        if employee_company:
            overtime_type = self.env['hr.overtime.type'].search([('type','=','rest_day'),('company_id','=',employee_company)], limit=1)
            if not overtime_type:
                overtime_type = self.env['hr.overtime.type'].search([('type','=','rest_day')], limit=1)
                if work_location:
                    overtime_type = self.env['hr.overtime.type'].search([('type','=','rest_day'),('company_id','=',employee_company),('work_location_id','=',work_location)], limit=1)
                    if not overtime_type:
                        if employee_company:
                            overtime_type = self.env['hr.overtime.type'].search([('type','=','rest_day'),('company_id','=',employee_company)], limit=1)
                            if not overtime_type:
                                overtime_type = self.env['hr.overtime.type'].search([('type','=','rest_day')], limit=1)    

                        
        return overtime_type
    
    
    
        
        
    def action_create_overtime(self):
        
        attendances=self.env['hr.attendance'].search([('employee_id.allow_overtime','=',True),('employee_id.company_id.id','!=',2),('is_overtime','=',False),('check_in','!=',False),('check_out','!=',False),('att_date','>=',self.date_start),('att_date','<=',self.date_end)])
        for att in attendances:
            day_min_ovt = 0
            overtime_rule = self.env['hr.overtime.rule'].search([('company_id','=',att.employee_id.company_id.id)])
            for rule in overtime_rule:
                if rule.rule_period == 'day' and rule.rule_type == 'minimum':
                    day_min_ovt = rule.hours
            overtime_limit = 0
            if att.shift_id:
                overtime_limit = att.rounded_hours - att.shift_id.hours_per_day
            else:
                overtime_limit = att.rounded_hours - 8
            overtime_type = self.get_normal_overtime_type(att.employee_id.company_id.id, att.employee_id.work_location_id.id)
            shift_schedule_lines = self.env['hr.shift.schedule.line'].search([('employee_id','=', att.employee_id.id),('rest_day','=',True),('date','=',att.att_date)])
            for rest_day in shift_schedule_lines:
                if rest_day.rest_day==True:
                    # get Rest Days overtime type
                    overtime_type = self.get_rest_days_overtime_type(att.employee_id.company_id.id, att.employee_id.work_location_id.id)
            for gazetted_day in att.shift_id.global_leave_ids:
                gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                if str(att.att_date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(att.att_date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                    # get gazetted overtime type
                    overtime_type = self.get_gazetted_overtime_type(att.employee_id.company_id.id, att.employee_id.work_location_id.id)
            if overtime_type.type=='gazetted':    
                vals = {
                        'employee_id': att.employee_id.id,
                        'company_id': att.employee_id.company_id.id,
                        'date':  att.att_date,
                        'date_from': att.check_in,
                        'date_to': att.check_out,
                        'hours': att.rounded_hours,
                        'actual_ovt_hours': att.rounded_hours,
                        'overtime_hours': overtime_limit if overtime_limit>0 else 0,
                        'overtime_type_id': overtime_type.id,
                    }
                overtime_lines = self.env['hr.overtime.request'].create(vals)
                att.update({
                    'is_overtime': True
                })
            elif overtime_type.type=='rest_day':
                vals = {
                        'employee_id': att.employee_id.id,
                        'company_id': att.employee_id.company_id.id,
                        'date':  att.att_date,
                        'date_from': att.check_in,
                        'date_to': att.check_out,
                        'hours': att.rounded_hours,
                        'actual_ovt_hours': att.rounded_hours,
                        'overtime_hours': overtime_limit if overtime_limit>0 else 0,
                        'overtime_type_id': overtime_type.id,
                    }
                overtime_lines = self.env['hr.overtime.request'].create(vals)
                att.update({
                    'is_overtime': True
                })
            else:
                if overtime_limit > 0 and overtime_limit > day_min_ovt and att.employee_id.cpl==False:
                    vals = {
                            'employee_id': att.employee_id.id,
                            'company_id': att.employee_id.company_id.id,
                            'date':  att.att_date,
                            'date_from': att.check_in,
                            'date_to': att.check_out,
                            'hours': att.rounded_hours,
                            'actual_ovt_hours': overtime_limit,
                            'overtime_hours': overtime_limit,
                            'overtime_type_id': overtime_type.id,
                        }
                    overtime_lines = self.env['hr.overtime.request'].create(vals)
                    att.update({
                        'is_overtime': True
                    })