# -*- coding: utf-8 -*-

import logging
import math



from collections import namedtuple

from datetime import datetime, date, timedelta, time
from dateutil.rrule import rrule, DAILY
from pytz import timezone, UTC

from odoo import api, fields, models, SUPERUSER_ID, tools
from odoo.addons.base.models.res_partner import _tz_get
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools.translate import _
from odoo.osv import expression
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger(__name__)

# Used to agglomerate the attendances in order to find the hour_from and hour_to
# See _compute_date_from_to
DummyAttendance = namedtuple('DummyAttendance', 'hour_from, hour_to, dayofweek, day_period, week_type')


class HolidaysRequest(models.Model):
    _inherit = 'hr.leave'

        
    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        if employee_id:
            shift_schedule_line = self.env['hr.shift.schedule.line'].sudo().search([('employee_id','=',employee_id),('date','>=',str(date_from)),('date','<=',str(date_to))])            
            tot_rest_days = 0
            gazetted_days_count = 0
            COUNT_1 = 0
            for shift_line in shift_schedule_line:
                shift = shift_line.first_shift_id
                if not shift:
                    shift = self.employee_id.shift_id
                if not shift:
                    shift = self.env['resource.calendar'].sudo().search([('shift_type','=','general'),('company_id','=',line.employee_id.company_id.id)], limit=1)
                for gazetted_day in shift.global_leave_ids:
                    gazetted_date_from = gazetted_day.date_from + relativedelta(hours=+5)
                    gazetted_date_to = gazetted_day.date_to + relativedelta(hours=+5)
                    if str(shift_line.date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(shift_line.date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                        gazetted_days_count += 1 
                if shift_line.rest_day == True:
                    for gazetted_day in shift.global_leave_ids:
                        gazetted_date_from = gazetted_day.date_from + relativedelta(hours=+5)
                        gazetted_date_to = gazetted_day.date_to + relativedelta(hours=+5)
                        if str(shift_line.date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(shift_line.date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                            tot_rest_days -= 1    
                    tot_rest_days += 1
            days = 0 
            if self.request_date_to and  self.request_date_from:   
                delta_days = (self.request_date_to - self.request_date_from).days  
                days = delta_days - tot_rest_days - gazetted_days_count + 1
            empshift = self.env['hr.employee'].search([('id','=',employee_id)], limit=1)
            hours = days * empshift.shift_id.hours_per_day if empshift.shift_id else 8
            return {'days': days, 'hours': hours}
        else:
            today_hours = self.env.company.resource_calendar_id.get_work_hours_count(
            datetime.combine(date_from.date(), time.min),
            datetime.combine(date_from.date(), time.max),
            False)

            hours = self.env.company.resource_calendar_id.get_work_hours_count(date_from, date_to)
            days = hours / (today_hours or HOURS_PER_DAY) if not self.request_unit_half else 0.5
            return {'days': days, 'hours': hours}
        
    def action_compute_days(self):
        for line in self:
            shift_schedule_line = self.env['hr.shift.schedule.line'].sudo().search([('employee_id','=',line.employee_id.id),('date','>=',str(line.request_date_from)),('date','<=',str(line.request_date_to))])
            tot_rest_days = 0
            gazetted_days_count = 0
            COUNT_1 = 0
            for shift_line in shift_schedule_line:
                shift = shift_line.first_shift_id
                if not shift:
                    shift = line.employee_id.shift_id
                if not shift:
                    shift = self.env['resource.calendar'].sudo().search([('shift_type','=','general'),('company_id','=',line.employee_id.company_id.id)], limit=1)

                for gazetted_day in shift.global_leave_ids:
                    gazetted_date_from = gazetted_day.date_from + relativedelta(hours=+5)
                    gazetted_date_to = gazetted_day.date_to + relativedelta(hours=+5)
                    if str(shift_line.date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(shift_line.date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):

                        gazetted_days_count += 1 

                if shift_line.rest_day == True:
                    for gazetted_day in shift.global_leave_ids:
                        gazetted_date_from = gazetted_day.date_from + relativedelta(hours=+5)
                        gazetted_date_to = gazetted_day.date_to + relativedelta(hours=+5)
                        if str(shift_line.date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(shift_line.date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                            tot_rest_days -= 1    

                    tot_rest_days += 1
            days=0    
            if self.request_date_to and  self.request_date_from:
                delta_days = (self.request_date_to - self.request_date_from).days  
                days = delta_days - tot_rest_days - gazetted_days_count + 1
            
            line.update({
                  'number_of_days': days
                })   
                
    
    category_id = fields.Many2one('approval.category', related='holiday_status_id.category_id', string="Approval Category", default=lambda self: self.holiday_status_id.category_id.id, required=False, readonly=True)
    leave_category = fields.Selection([
        ('day', 'Day'),
        ('half_day', 'Half Day'),
        ('hours', 'Short leave'),
        ], string='Leave Category', tracking=True)
    approval_request_id = fields.Many2one('approval.request', string='Approval Request', copy=False, readonly=True)
    request_status = fields.Selection(related='approval_request_id.request_status')
    attachment_id = fields.Many2many('ir.attachment', relation="files_rel_leave",
                                            column1="doc_id",
                                            column2="attachment_id",
                                            string="Attachment")
    approve_date = fields.Date(string='Approve Date')
    
    
    def action_validate(self):
       
        res = super(HolidaysRequest, self).action_validate()
        self.update({
            'approve_date': fields.date.today()
        })
        return res
    
    
    def action_cancel(self):
        for leave in self:
            leave.update({
                'state': 'cancel'
            })
            leave_approval = self.env['approval.request'].search([('leave_id','=',leave.id)], limit=1)
            leave_approval.action_cancel()
    
    
    @api.constrains('attachment_id')
    def onchange_attachment(self):
        if not self.attachment_id:
            if self.holiday_status_id.attachment  == True:
                diff = self.number_of_days
                if diff > self.holiday_status_id.attachment_validity:
                    raise ValidationError(_("Please Add Your Medical Certificate !"))
           
    
    
    
    def _get_date_from_to(self):
        for holiday in self:
            if holiday.request_date_from and holiday.request_date_to and holiday.request_date_from > holiday.request_date_to:
                holiday.request_date_to = holiday.request_date_from
            if not holiday.request_date_from:
                holiday.date_from = False
            elif not holiday.request_unit_half and not holiday.request_unit_hours and not holiday.request_date_to:
                holiday.date_to = False
            else:
                if holiday.request_unit_half or holiday.request_unit_hours:
                    holiday.request_date_to = holiday.request_date_from
                resource_calendar_id = holiday.employee_id.resource_calendar_id or self.env.company.resource_calendar_id
                domain = [('calendar_id', '=', resource_calendar_id.id), ('display_type', '=', False)]
                attendances = self.env['resource.calendar.attendance'].read_group(domain, ['ids:array_agg(id)', 'hour_from:min(hour_from)', 'hour_to:max(hour_to)', 'week_type', 'dayofweek', 'day_period'], ['week_type', 'dayofweek', 'day_period'], lazy=False)

                # Must be sorted by dayofweek ASC and day_period DESC
                attendances = sorted([DummyAttendance(group['hour_from'], group['hour_to'], group['dayofweek'], group['day_period'], group['week_type']) for group in attendances], key=lambda att: (att.dayofweek, att.day_period != 'morning'))

                default_value = DummyAttendance(0, 0, 0, 'morning', False)

                if resource_calendar_id.two_weeks_calendar:
                    # find week type of start_date
                    start_week_type = int(math.floor((holiday.request_date_from.toordinal() - 1) / 7) % 2)
                    attendance_actual_week = [att for att in attendances if att.week_type is False or int(att.week_type) == start_week_type]
                    attendance_actual_next_week = [att for att in attendances if att.week_type is False or int(att.week_type) != start_week_type]
                    # First, add days of actual week coming after date_from
                    attendance_filtred = [att for att in attendance_actual_week if int(att.dayofweek) >= holiday.request_date_from.weekday()]
                    # Second, add days of the other type of week
                    attendance_filtred += list(attendance_actual_next_week)
                    # Third, add days of actual week (to consider days that we have remove first because they coming before date_from)
                    attendance_filtred += list(attendance_actual_week)

                    end_week_type = int(math.floor((holiday.request_date_to.toordinal() - 1) / 7) % 2)
                    attendance_actual_week = [att for att in attendances if att.week_type is False or int(att.week_type) == end_week_type]
                    attendance_actual_next_week = [att for att in attendances if att.week_type is False or int(att.week_type) != end_week_type]
                    attendance_filtred_reversed = list(reversed([att for att in attendance_actual_week if int(att.dayofweek) <= holiday.request_date_to.weekday()]))
                    attendance_filtred_reversed += list(reversed(attendance_actual_next_week))
                    attendance_filtred_reversed += list(reversed(attendance_actual_week))

                    # find first attendance coming after first_day
                    attendance_from = attendance_filtred[0]
                    # find last attendance coming before last_day
                    attendance_to = attendance_filtred_reversed[0]
                else:
                    # find first attendance coming after first_day
                    attendance_from = next((att for att in attendances if int(att.dayofweek) >= holiday.request_date_from.weekday()), attendances[0] if attendances else default_value)
                    # find last attendance coming before last_day
                    attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= holiday.request_date_to.weekday()), attendances[-1] if attendances else default_value)

                compensated_request_date_from = holiday.request_date_from
                compensated_request_date_to = holiday.request_date_to

                if holiday.request_unit_half:
                    if holiday.request_date_from_period == 'am':
                        hour_from = float_to_time(attendance_from.hour_from)
                        hour_to = float_to_time(attendance_from.hour_to)
                    else:
                        hour_from = float_to_time(attendance_to.hour_from)
                        hour_to = float_to_time(attendance_to.hour_to)
                elif holiday.request_unit_hours:
                    hour_from = float_to_time(float(holiday.request_hour_from))
                    hour_to = float_to_time(float(holiday.request_hour_to))
                elif holiday.request_unit_custom:
                    hour_from = holiday.date_from.time()
                    hour_to = holiday.date_to.time()
                    compensated_request_date_from = holiday._adjust_date_based_on_tz(holiday.request_date_from, hour_from)
                    compensated_request_date_to = holiday._adjust_date_based_on_tz(holiday.request_date_to, hour_to)
                else:
                    hour_from = float_to_time(attendance_from.hour_from)
                    hour_to = float_to_time(attendance_to.hour_to)

                holiday.date_from = timezone(holiday.tz).localize(datetime.combine(compensated_request_date_from, hour_from)).astimezone(UTC).replace(tzinfo=None)
                holiday.date_to = timezone(holiday.tz).localize(datetime.combine(compensated_request_date_to, hour_to)).astimezone(UTC).replace(tzinfo=None)
    
    

    
    
    @api.model_create_multi
    def create(self, vals_list):
        """ Override to avoid automatic logging of creation """
        if not self._context.get('leave_fast_create'):
            leave_types = self.env['hr.leave.type'].browse([values.get('holiday_status_id') for values in vals_list if values.get('holiday_status_id')])
            mapped_validation_type = {leave_type.id: leave_type.leave_validation_type for leave_type in leave_types}

            for values in vals_list:
                employee_id = values.get('employee_id', False)
                leave_type_id = values.get('holiday_status_id')
                # Handle automatic department_id
                if not values.get('department_id'):
                    values.update({'department_id': self.env['hr.employee'].browse(employee_id).department_id.id})

                # Handle no_validation
                if mapped_validation_type[leave_type_id] == 'no_validation':
                    values.update({'state': 'confirm'})

                # Handle multi approvals
                if mapped_validation_type[leave_type_id] == 'approvals':
                    values.update({'state': 'confirm'})
            
                if 'state' not in values:
                    # To mimic the behavior of compute_state that was always triggered, as the field was readonly
                    values['state'] = 'confirm' if mapped_validation_type[leave_type_id] != 'no_validation' else 'draft'

                # Handle double validation
                if mapped_validation_type[leave_type_id] == 'both':
                    self._check_double_validation_rules(employee_id, values.get('state', False))

        holidays = super(HolidaysRequest, self.with_context(mail_create_nosubscribe=True)).create(vals_list)

        for holiday in holidays:
            if not self._context.get('leave_fast_create'):
                # Everything that is done here must be done using sudo because we might
                # have different create and write rights
                # eg : holidays_user can create a leave request with validation_type = 'manager' for someone else
                # but they can only write on it if they are leave_manager_id
                holiday_sudo = holiday.sudo()
                holiday_sudo.add_follower(employee_id)
                if holiday.validation_type == 'manager':
                    holiday_sudo.message_subscribe(partner_ids=holiday.employee_id.leave_manager_id.partner_id.ids)
                if holiday.validation_type == 'no_validation':
                    # Automatic validation should be done in sudo, because user might not have the rights to do it by himself
                    holiday_sudo.action_validate()
                    holiday_sudo.message_subscribe(partner_ids=[holiday._get_responsible_for_approval().partner_id.id])
                    holiday_sudo.message_post(body=_("The time off has been automatically approved"), subtype_xmlid="mail.mt_comment") # Message from OdooBot (sudo)
                elif holiday.validation_type == 'approvals':
                    #holiday_sudo.action_validate()
                    holiday_sudo.action_create_approval_request()
                elif not self._context.get('import_file'):
                    holiday_sudo.activity_update()
            #holiday._get_date_from_to()  
            holiday._get_duration_update_approval()  
            holiday.action_validate_leave_period()
            holiday.action_onchange_attachment()  
        return holidays


    
    def action_onchange_attachment(self):
        if not self.attachment_id:
            if self.holiday_status_id.attachment  == True:
                diff = self.number_of_days
                if diff >= self.holiday_status_id.attachment_validity:
                    raise ValidationError(_("Please Add Your Medical Certificate !"))
           
    
    def action_validate_leave_period(self):
        restrict_date = '2021-07-16'
        for line in self:
            if str(line.request_date_from)  < restrict_date:

                raise UserError('Not Allow to Enter Leave Request before 16 JULY 2021!')
    
    def _get_duration_update_approval(self):
        for line in self:
            if line.approval_request_id:
                duration_type = ' '
                if line.leave_category == 'day':
                    duration_type = 'Days' 
                elif line.leave_category == 'half_day':
                    duration_type = 'Half Day' 
                elif line.leave_category == 'hours':
                    duration_type = 'Short leave'     
                line.approval_request_id.update({
                    'reason': ' Leave Type:  ' + str(line.holiday_status_id.name)+"\n"+' Duration type:  '+str(duration_type)+"\n"+' Request from:      '+str(line.request_date_from.strftime("%d %b %Y "))+ "\n" +' Request To:  '+str(line.request_date_to.strftime("%d %b %Y"))+ "\n" +' Duration :  '+str(line.number_of_days) +' Days'+ "\n"  +"\n" +"\n" + ' Remarks:   ' +str(line.name)+"\n", 
                })
    
    @api.depends('request_status','approval_request_id.request_status')
    @api.onchange('request_status','approval_request_id.request_status')
    def _onchange_request_status(self):
        if self.request_status == 'approved' or self.approval_request_id.request_status == 'approved':
            self.action_validate()
    
    @api.depends('holiday_status_id')
    def _compute_state(self):
        for holiday in self:
            if self.env.context.get('unlink') and holiday.state == 'draft':
                # Otherwise the record in draft with validation_type in (hr, manager, both) will be set to confirm
                # and a simple internal user will not be able to delete his own draft record
                holiday.state = 'draft'
            else:
                holiday.state = 'confirm' if holiday.validation_type not in ('no_validation','approvals') else 'draft'
                
    
    def action_confirm1(self):
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(_('Time off request must be in Draft state ("To Submit") in order to confirm it.'))
        self.write({'state': 'confirm'})
        holidays = self.filtered(lambda leave: leave.validation_type in ['no_validation','approvals'])
        if holidays:
            # Automatic validation should be done in sudo, because user might not have the rights to do it by himself
            holidays.sudo().action_validate()
        self.activity_update()
        return True
    
    def action_confirm2(self):
        result = super(HolidaysRequest, self).action_confirm()
        if self.category_id:
            self.action_create_approval_request()
        return result
        
    def action_create_approval_request(self):
        approver_ids  = []
        
        request_list = []
        for line in self:
            duration_type = ' '
            if line.leave_category == 'day':
                duration_type = 'Days' 
            elif line.leave_category == 'half_day':
                duration_type = 'Half Day' 
            elif line.leave_category == 'hours':
                duration_type = 'Short leave'     
                
            request_list.append({
                'name':  str(line.employee_id.name) ,
                'request_owner_id': line.employee_id.user_id.id or line.user_id.id,
                'category_id': line.category_id.id,
                'leave_id': line.id,
                'reason': ' Leave Type:  ' + str(line.holiday_status_id.name)+"\n"+' Request from:      '+str(line.request_date_from.strftime("%d %b %Y "))+ "\n" +' Request To:  '+str(line.request_date_to.strftime("%d %b %Y"))+ "\n" +' Duration :  '+str(line.number_of_days) +' Days'+ "\n" +' Duration type:  '+str(duration_type)+"\n" +"\n" +"\n" + ' Remarks:   ' +str(line.name)+"\n",
                'request_status': 'new',
            })
            approval_request_id = self.env['approval.request'].create(request_list)
            approval_request_id._onchange_category_id()
            approval_request_id.action_confirm()
            approval_request_id.action_date_confirm_update()
            line.approval_request_id = approval_request_id.id
            if line.holiday_status_id.is_ceo_approval == True:
                if line.employee_id.company_id.manager_id.user_id.id != line.employee_id.user_id.id:
                    approver_vals = {
                        'user_id': line.employee_id.company_id.manager_id.user_id.id,
                        'request_id': approval_request_id.id,
                    }
                    approver_lines = self.env['approval.approver'].sudo().create(approver_vals)


