from odoo import models, api, fields, _
from odoo.exceptions import ValidationError, UserError
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
from dateutil.relativedelta import relativedelta
from odoo.tools.translate import _
from odoo.osv import expression

_logger = logging.getLogger(__name__)

# Used to agglomerate the attendances in order to find the hour_from and hour_to
# See _compute_date_from_to
DummyAttendance = namedtuple('DummyAttendance', 'hour_from, hour_to, dayofweek, day_period, week_type')



class HrShiftSchedule(models.Model):
    _inherit = 'hr.shift.schedule'
    
    @api.model
    def action_generate_leave(self):
        for line in self:
            if line.state == 'posted':
                leave_type = self.env['hr.rest.day.config'].search([], limit=1)
                if line.company_id: 
                    leave_type = self.env['hr.rest.day.config'].search([('company_id','=',line.company_id.id)], limit=1)
                if not leave_type:
                    raise UserError(('Please Define Rest Day Configuration!'))
                else: 
                    for shift_line in line.schedule_line_ids:
                        if shift_line.rest_day == True and shift_line.leave_created == False:
                            hours_from = shift_line.date + relativedelta(hours =+ 1) 
                            hours_to = shift_line.date + relativedelta(hours =+ 9)
                            day_line = 0
                            if shift_line.day.name == 'Monday':
                                day_line = 0 
                            if shift_line.day.name == 'Tuesday':
                                day_line = 1 
                            if shift_line.day.name == 'Wednesday':
                                day_line = 2 
                            if shift_line.day.name == 'Thursday':
                                day_line = 3 
                            if shift_line.day.name == 'Friday':
                                day_line = 4 
                            if shift_line.day.name == 'Saturday':
                                day_line = 5 
                            if shift_line.day.name == 'Sunday':
                                day_line = 6     
                            for attendee in line.employee_id.shift_id.attendance_ids:
                                hours_from = shift_line.date + relativedelta(hours =+ attendee.hour_from)   
                                hours_to = shift_line.date + relativedelta(hours =+ attendee.hour_to)
                                if day_line == attendee.dayofweek:
                                    hours_from = shift_line.date + relativedelta(hours =+ attendee.hour_from)   
                                    hours_to = shift_line.date + relativedelta(hours =+ attendee.hour_to)
                                    
                            vals = {
                            'holiday_status_id': leave_type.leave_type_id.id,
                            'employee_id': line.employee_id.id, 
                            'holiday_type': 'employee', 
                            'request_date_from': shift_line.date,
                            'number_of_days': 1,   
                            'request_date_to': shift_line.date,
                             'date_from': hours_from,
                             'date_to': hours_to,   
                            }
                            leave = self.env['hr.leave'].create(vals)
                            leave.action_date_from_to()
                            if leave.number_of_days == 0:
                                if leave.holiday_status_id.request_unit == 'day':
                                    leave.update({
                                        'number_of_days': 1
                                    })
                                elif leave.holiday_status_id.request_unit == 'hour': 
                                    leave.update({
                                        'number_of_days': shift_line.employee_id.shift_id.hours_per_day if shift_line.employee_id.shift_id.hours_per_day else 8
                                    })
                                else: 
                                    leave.update({
                                        'number_of_days': shift_line.employee_id.shift_id.hours_per_day if shift_line.employee_id.shift_id.hours_per_day else 8
                                    })        
                            leave.action_approve()
                        shift_line.update({
                         'leave_created': True
                        })
                
        
        
class HrScheduleLine(models.Model):
    _inherit = 'hr.shift.schedule.line'    
    
    leave_created = fields.Boolean(string="Leave Created")
    
