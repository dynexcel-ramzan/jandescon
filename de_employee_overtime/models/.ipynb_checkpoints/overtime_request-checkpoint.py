# -*- coding: utf-8 -*-

from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.resource.models.resource import HOURS_PER_DAY
import math

class HrOverTime(models.Model):
    _name = 'hr.overtime.request'
    _description = "HR Overtime Request"
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    
    
    
    @api.model_create_multi
    def create(self, vals_list):
        rslt = super(HrOverTime, self).create(vals_list)
        rslt.action_leave_allocation()
        return rslt   
    
    
    def action_leave_allocation(self):
        leave_type = 0
        leave_total_hours = 0
        leave_period = ' '
        shift = []
        for line in self:
            shift_line=self.env['hr.shift.schedule.line'].search([('employee_id','=', line.employee_id.id),('date','=',line.date),('state','=','posted')], limit=1)
            if shift_line:
                shift= shift_line.first_shift_id
            if not shift:
                shift =  line.employee_id.shift_id
            if not shift:
                shift =  self.env['resource.calendar'].search([('company_id','=', line.employee_id.company_id.id)], limit=1)
            for ovt_type_line in line.overtime_type_id.type_line_ids:
                if ovt_type_line.compansation == 'leave':
                    if (shift.hours_per_day/2) <= line.hours and ovt_type_line.leave_type=='half_day':
                        leave_type = ovt_type_line.leave_type_id.id     
                        leave_period = ovt_type_line.leave_type
                    elif (shift.hours_per_day) <= line.hours and ovt_type_line.leave_type=='full_day':
                        leave_type = ovt_type_line.leave_type_id.id     
                        leave_period = ovt_type_line.leave_type    
        if leave_type > 0:
            leave_total_hours = 0
        if leave_period == 'half_day':
            leave_total_hours = ((shift.hours_per_day)/2)  
        elif leave_period == 'full_day':
            leave_total_hours = shift.hours_per_day
        if leave_total_hours > 0: 
            vals = {
                'holiday_status_id': leave_type,
                'employee_id': line.employee_id.id, 
                'overtime_id': line.id,
                'request_date': fields.date.today(),
                'holiday_type': 'employee',
                'allocation_type': 'regular',
                'ovt_date': line.date,
                'number_of_hours_calc': leave_total_hours,
                'name':  "Allocation Created From Overtime Compensation Type "+str(line.overtime_type_id.name)+' ('+str(line.date)+')', 
                        }
            timeoff = self.env['hr.leave.allocation'].create(vals)
            if leave_period == 'half_day':
                timeoff.update({
               'number_of_days_display': 0.5,
                'number_of_days': 0.5,
               'number_of_hours_calc': leave_total_hours,
               })
            timeoff.action_create_approval_request_allocation()
    
    def action_submit(self):
        for line in self:
            if line.state == 'draft':
                line.update({
                    'state': 'to_approve'
                })
        
    def action_cancel(self):
        for line in self:
            if line.state not in ['approved', 'paid']:
                line.update({
                    'state': 'close'
                }) 
            
    def unlink(self):
        for ovt in self:
            if ovt.state not in ('draft','close'):
                raise UserError(_('You cannot delete an Document  which is not draft or cancelled. '))
     
            return super(HrOverTime, self).unlink()  
    
    
    def generate_normal_overtime_compansation(self):
        """
         Generate Overtime Entries 
         1- By Normal Overtime type
        """
        for line in self:
            ot_amount = 0.0
            nrate = 0
            for compansation in line.overtime_type_id.type_line_ids:
                if line.overtime_hours >= compansation.ot_hours:
                    if compansation.compansation == 'payroll':
                        if compansation.rate_type == 'fix_amount':
                            ot_amount = compansation.rate * line.overtime_hours 
                        elif compansation.rate_type == 'percent':
                            contract = self.env['hr.contract'].search([('employee_id','=',line.employee_id.id),('state','=','open')], limit=1)   
                            ot_hour_amount = (contract.wage * compansation.rate_percent ) /(compansation.hours_per_day * compansation.month_day)
                            nrate = compansation.rate_percent
                            ot_amount = ot_hour_amount * line.overtime_hours
            total_amount = ot_amount
            if  line.overtime_type_id.type == 'normal': 
                if total_amount > 0:
                    entry_vals = {
                            'employee_id': line.employee_id.id,
                            'date': line.date,
                            'amount': total_amount ,
                            'company_id':  line.company_id.id,
                            'overtime_hours': line.overtime_hours,
                            'overtime_type_id': line.overtime_type_id.id,
                            'remarks': '@rate '+ str(nrate)
                    }
                    overtime_entry = self.env['hr.overtime.entry'].create(entry_vals)
                


                
    def generate_overtime_compansation(self):
        """
         Generate Overtime Entries 
         1- By Using Overtime type
         2- Gazetted and Rest Day
        """
        for line in self:
            if line.employee_id.cpl == False:
                single_ot_amount = 0
                double_ot_amount = 0
                single_hour_limit = 0
                double_rate_ot_hours = 0
                single_ot_hour_amount = 0
                double_ot_hour_amount = 0
                grate2 = ' '
                grate = ' '
                double_rate_line=self.env['hr.overtime.type.line'].search([('overtime_type_id','=',line.overtime_type_id.id),('compansation','=', 'payroll'),('ot_hours','<=', line.overtime_hours),('entry_type_id','=','double'),('rate_type','=','percent')], order='ot_hours desc', limit=1)
                single_rate_line=self.env['hr.overtime.type.line'].search([('overtime_type_id','=',line.overtime_type_id.id),('compansation','=', 'payroll'),('ot_hours','<=', line.overtime_hours),('entry_type_id','=','single'),('rate_type','=','percent')], order='ot_hours desc', limit=1)    
                contract = self.env['hr.contract'].search([('employee_id','=',line.employee_id.id),('state','=','open')], limit=1)
                single_fixed_amount =self.env['hr.overtime.type.line'].search([('overtime_type_id','=',line.overtime_type_id.id),('compansation','=', 'payroll'),('ot_hours','<=', line.overtime_hours),('entry_type_id','=','single'),('rate_type','=','fix_amount')], order='ot_hours desc', limit=1)
                double_fixed_amount =self.env['hr.overtime.type.line'].search([('overtime_type_id','=',line.overtime_type_id.id),('compansation','=', 'payroll'),('ot_hours','<=', line.overtime_hours),('entry_type_id','=','double'),('rate_type','=','fix_amount')], order='ot_hours desc', limit=1)
                if double_rate_line and single_rate_line:
                    single_hour_limit =  single_rate_line.ot_hours
                    double_rate_ot_hours = line.overtime_hours - single_rate_line.ot_hours
                    double_ot_hour_amount = (contract.wage * double_rate_line.rate_percent ) /(double_rate_line.hours_per_day * double_rate_line.month_day)
                    single_ot_hour_amount = (contract.wage * single_rate_line.rate_percent ) /(single_rate_line.hours_per_day * single_rate_line.month_day)
                    grate2 = double_rate_line.rate_percent
                    grate  = single_rate_line.rate_percent
                elif  single_rate_line:
                    single_hour_limit =  line.overtime_hours
                    single_ot_hour_amount = (contract.wage * single_rate_line.rate_percent ) /(single_rate_line.hours_per_day * single_rate_line.month_day)
                    grate  = single_rate_line.rate_percent
                else:
                    if single_fixed_amount and double_fixed_amount:
                        single_hour_limit =  single_fixed_amount.ot_hours
                        double_rate_ot_hours = line.overtime_hours - single_fixed_amount.ot_hours 
                        single_ot_hour_amount = single_fixed_amount.rate
                        double_ot_hour_amount = double_fixed_amount.rate
                    elif single_fixed_amount:
                        single_hour_limit =  line.overtime_hours 
                        single_ot_hour_amount = single_fixed_amount.rate                    

                single_ot_amount =  single_ot_hour_amount * single_hour_limit
                double_ot_amount =  double_ot_hour_amount * double_rate_ot_hours
                if single_ot_amount > 0:
                    if line.employee_id.cpl == False:
                        entry_vals = {
                                'employee_id': line.employee_id.id,
                                'date': line.date,
                                'amount': round(single_ot_amount) ,
                                'company_id':  line.company_id.id,
                                'overtime_hours': single_hour_limit,
                                'overtime_type_id': line.overtime_type_id.id,
                                'remarks': '@rate '+str(grate)                                    
                                              }
                        overtime_entry_single = self.env['hr.overtime.entry'].create(entry_vals)
                if double_ot_amount > 0:
                    if line.employee_id.cpl == False:
                        entry_vals = {
                                'employee_id': line.employee_id.id,
                                'date': line.date,
                                'amount': round(double_ot_amount) ,
                                'company_id':  line.company_id.id,
                                'overtime_hours': double_rate_ot_hours,
                                'overtime_type_id': line.overtime_type_id.id,
                                'remarks': '@rate '+str(grate2) ,
                                                }
                        overtime_entry_double = self.env['hr.overtime.entry'].create(entry_vals)



    def action_approve(self):
        for line in self:
            if line.state == 'to_approve' and line.employee_id.cpl==False:
                ot_amount = 0
                gazetted_hours = 0
                nrate = 0
                leave_period = ' '
                leave_type = 0
                if line.overtime_type_id.type == 'normal':
                    line.generate_normal_overtime_compansation()    
                elif line.overtime_type_id.type == 'rest_day':
                    line.generate_overtime_compansation()                                    
                elif  line.overtime_type_id.type == 'gazetted': 
                    line.generate_overtime_compansation() 
                line.update({
                        'state': 'approved'
                        })     
            else:
                line.update({
                   'state': 'approved'
                })  
                
    
    def action_refuse(self):
        for line in self:
            line.update({
                'state': 'refused'
            })
     
    
    employee_id = fields.Many2one('hr.employee', string="Name")
    employee_number = fields.Char(string='Employee Number')
    date_from = fields.Datetime('Date From', required=True)
    company_id = fields.Many2one('res.company', string="Company")
    date = fields.Date('Date', required=True)
    date_to = fields.Datetime('Date to', required=True)
    overtime_type_id = fields.Many2one('hr.overtime.type', string="Overtime Type", domain="['|',('company_id','=',company_id), ('company_id','=',False)]")
    hours = fields.Float('Total Hours')
    overtime_hours = fields.Float('Feeded Hours')
    actual_ovt_hours = fields.Float('Actual Overtime Hours', readonly=True, )
    attendance_ids = fields.Many2many('hr.attendance', string="Attendance")
    remarks = fields.Char(string="Remarks")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),        
        ('paid', 'Paid'),
        ('close', 'Cancelled'),
        ('refused', 'Refused')], string="Status",
                             default="draft")
    
    work_location_id = fields.Many2one('hr.work.location', string="Work Location", compute='_compute_employee_location')
    workf_location_id = fields.Many2one('hr.work.location', string="Work Location")

    @api.depends('employee_id')
    def _compute_employee_location(self):
        for line in self:
            line.update({
               'work_location_id': line.employee_id.work_location_id.id,
               'workf_location_id': line.employee_id.work_location_id.id,
                }) 
     
    @api.constrains('employee_id')
    def _check_employee_id(self):  
        for line in self:
            line.update({
                'employee_number': line.employee_id.emp_number,
            })  

    @api.constrains('overtime_hours')
    def _check_leave_type(self):
        for line in self:
            if line.overtime_hours:
                if line.overtime_hours > line.actual_ovt_hours:
                    line.overtime_hours = line.actual_ovt_hours

    
    


    @api.depends('hours')
    def _get_overtime_hours(self):
        for ovt in self:
            overtime_hours = ovt.hours - ovt.employee_id.shift_id.hours_per_day    
            ovt.actual_ovt_hours = overtime_hours
            
    @api.depends('date_from', 'date_to')
    def _get_days(self):
        for recd in self:
            if recd.date_from and recd.date_to:
                if recd.date_from > recd.date_to:
                    raise ValidationError('Start Date must be less than End Date')
        for sheet in self:
            if sheet.date_from and sheet.date_to:
                start_dt = fields.Datetime.from_string(sheet.date_from)
                finish_dt = fields.Datetime.from_string(sheet.date_to)
                s = finish_dt - start_dt
                difference = relativedelta.relativedelta(finish_dt, start_dt)
                hours = difference.hours
                minutes = difference.minutes
                days_in_mins = s.days * 24 * 60
                hours_in_mins = hours * 60
                days_no = ((days_in_mins + hours_in_mins + minutes) / (24 * 60))

                diff = sheet.date_to - sheet.date_from
                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds // 3600
                sheet.update({
                    'hours': hours ,
                })

    