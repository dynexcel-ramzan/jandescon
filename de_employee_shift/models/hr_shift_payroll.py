# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, _, tools
from datetime import datetime, time
import datetime
import math
from pytz import utc
from odoo.tools.float_utils import float_round
from collections import namedtuple
from collections import defaultdict
import math
from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY, WEEKLY
from functools import partial
from itertools import chain
from pytz import timezone, utc

from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import _tz_get
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_round

from odoo.tools import date_utils, float_utils

# Default hour per day value. The one should
# only be used when the one from the calendar
# is not available.
HOURS_PER_DAY = 8
# This will generate 16th of days
ROUNDING_FACTOR = 16


def _boundaries(intervals, opening, closing):
    """ Iterate on the boundaries of intervals. """
    for start, stop, recs in intervals:
        if start < stop:
            yield (start, opening, recs)
            yield (stop, closing, recs)


class Intervals(object):
    """ Collection of ordered disjoint intervals with some associated records.
        Each interval is a triple ``(start, stop, records)``, where ``records``
        is a recordset.
    """
    def __init__(self, intervals=()):
        self._items = []
        if intervals:
            # normalize the representation of intervals
            append = self._items.append
            starts = []
            recses = []
            for value, flag, recs in sorted(_boundaries(intervals, 'start', 'stop')):
                if flag == 'start':
                    starts.append(value)
                    recses.append(recs)
                else:
                    start = starts.pop()
                    if not starts:
                        append((start, value, recses[0].union(*recses)))
                        recses.clear()

    def __bool__(self):
        return bool(self._items)

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __reversed__(self):
        return reversed(self._items)

    def __or__(self, other):
        """ Return the union of two sets of intervals. """
        return Intervals(chain(self._items, other._items))

    def __and__(self, other):
        """ Return the intersection of two sets of intervals. """
        return self._merge(other, False)

    def __sub__(self, other):
        """ Return the difference of two sets of intervals. """
        return self._merge(other, True)

    def _merge(self, other, difference):
        """ Return the difference or intersection of two sets of intervals. """
        result = Intervals()
        append = result._items.append

        # using 'self' and 'other' below forces normalization
        bounds1 = _boundaries(self, 'start', 'stop')
        bounds2 = _boundaries(other, 'switch', 'switch')

        start = None                    # set by start/stop
        recs1 = None                    # set by start
        enabled = difference            # changed by switch
        for value, flag, recs in sorted(chain(bounds1, bounds2)):
            if flag == 'start':
                start = value
                recs1 = recs
            elif flag == 'stop':
                if enabled and start < value:
                    append((start, value, recs1))
                start = None
            else:
                if not enabled and start is not None:
                    start = value
                if enabled and start is not None and start < value:
                    append((start, value, recs1))
                enabled = not enabled

        return result







class HrPayroll(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        def was_on_leave_interval(employee_id, date_from, date_to):
            date_from = fields.Datetime.to_string(date_from)
            date_to = fields.Datetime.to_string(date_to)
            return self.env['hr.leave'].search([
                ('state', '=', 'validate'),
                ('employee_id', '=', employee_id),
                # ('type', '=', 'remove'),
                ('date_from', '<=', date_from),
                ('date_to', '>=', date_to)
            ], limit=1)

        res = []
        # fill only if the contract as a working schedule linked
        uom_day = self.env.ref('product.product_uom_day', raise_if_not_found=False)
        for contract in contract_ids:
            uom_hour = self.env.ref('product.product_uom_hour', raise_if_not_found=False)
            interval_data = []
            holidays = self.env['hr.leave']
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            leaves = {}

            # Gather all intervals and holidays
            for days in contract.shift_schedule:
                start_date = datetime.datetime.strptime(str(days.start_date), tools.DEFAULT_SERVER_DATE_FORMAT)
                end_date = datetime.datetime.strptime(str(days.end_date), tools.DEFAULT_SERVER_DATE_FORMAT)
                nb_of_days = (days.end_date - days.start_date).days + 1
                for day in range(0, nb_of_days):
                    working_intervals_on_day = days.hr_shift._get_day_work_intervals(
                        start_date + timedelta(days=day))
                    for interval in working_intervals_on_day:
                        interval_data.append(
                            (interval, was_on_leave_interval(contract.employee_id.id, interval[0], interval[1])))

            # Extract information from previous data. A working interval is considered:
            # - as a leave if a hr.holiday completely covers the period
            # - as a working period instead
            for interval, holiday in interval_data:
                holidays |= holiday
                hours = (interval[1] - interval[0]).total_seconds() / 3600.0
                if holiday:
                    # if he was on leave, fill the leaves dict
                    if holiday.holiday_status_id.name in leaves:
                        leaves[holiday.holiday_status_id.name]['number_of_hours'] += hours
                    else:
                        leaves[holiday.holiday_status_id.name] = {
                            'name': holiday.holiday_status_id.name,
                            'sequence': 5,
                            'code': holiday.holiday_status_id.name,
                            'number_of_days': 0.0,
                            'number_of_hours': hours,
                            'contract_id': contract.id,
                        }
                else:
                    # add the input vals to tmp (increment if existing)
                    attendances['number_of_hours'] += hours
            # Clean-up the results
            leaves = [value for key, value in leaves.items()]
            for data in [attendances] + leaves:
                data['number_of_days'] = uom_hour._compute_quantity(data['number_of_hours'], uom_day) \
                    if uom_day and uom_hour \
                    else data['number_of_hours'] / 8.0
                res.append(data)
        return res


class Calendar(models.Model):
    _inherit = 'resource.calendar'
    _interval_obj = namedtuple('Interval', ('start_datetime', 'end_datetime', 'data'))
    
    shift_type = fields.Selection([
        ('general', 'General'),
        ('morning', 'Morning'),
        ('evening', 'Evening'),
        ('night', 'Night'),
        
    ], string='Shift Type',copy=True, required=True)
    
    
    def _check_overlap(self, attendance_ids):
        """ attendance_ids correspond to attendance of a week,
            will check for each day of week that there are no superimpose. """
        result = []
        for attendance in attendance_ids.filtered(lambda att: not att.date_from and not att.date_to):
            # 0.000001 is added to each start hour to avoid to detect two contiguous intervals as superimposing.
            # Indeed Intervals function will join 2 intervals with the start and stop hour corresponding.
            result.append((int(attendance.dayofweek) * 24 + attendance.hour_from + 0.000001, int(attendance.dayofweek) * 24 + attendance.hour_to, attendance))

        if len(Intervals(result)) != len(result):
            if self.shift_type != 'night':
                raise ValidationError(_("Attendances can't overlap."))
                
                
    def _compute_hours_per_day(self, attendances):
        if not attendances:
            return 0

        hour_count = 0.0
        for attendance in attendances:
            if self.shift_type != 'night':
                hour_count += attendance.hour_to - attendance.hour_from
            elif self.shift_type == 'night':
                hour_count +=  (24 - attendance.hour_from)   + attendance.hour_to   

        if self.two_weeks_calendar:
            number_of_days = len(set(attendances.filtered(lambda cal: cal.week_type == '1').mapped('dayofweek')))
            number_of_days += len(set(attendances.filtered(lambda cal: cal.week_type == '0').mapped('dayofweek')))
        else:
            number_of_days = len(set(attendances.mapped('dayofweek')))

        return float_round(hour_count / float(number_of_days), precision_digits=2)
        
    

    def string_to_datetime(self, value):
        """ Convert the given string value to a datetime in UTC. """
        return utc.localize(fields.Datetime.from_string(value))

    def float_to_time(self, hours):
        """ Convert a number of hours into a time object. """
        if hours == 24.0:
            return time.max
        fractional, integral = math.modf(hours)
        return time(int(integral), int(float_round(60 * fractional, precision_digits=0)), 0)

    def _interval_new(self, start_datetime, end_datetime, kw=None):
        kw = kw if kw is not None else dict()
        kw.setdefault('attendances', self.env['resource.calendar.attendance'])
        kw.setdefault('leaves', self.env['resource.calendar.leaves'])
        return self._interval_obj(start_datetime, end_datetime, kw)

    
    def _get_day_work_intervals(self, day_date, start_time=None, end_time=None, compute_leaves=False,
                                resource_id=None):
        self.ensure_one()

        if not start_time:
            start_time = datetime.time.min
        if not end_time:
            end_time = datetime.time.max

        working_intervals = [att_interval for att_interval in
                             self._iter_day_attendance_intervals(day_date, start_time, end_time)]

        # filter according to leaves
        if compute_leaves:
            leaves = self._get_leave_intervals(
                resource_id=resource_id,
                start_datetime=datetime.datetime.combine(day_date, start_time),
                end_datetime=datetime.datetime.combine(day_date, end_time))
            working_intervals = [
                sub_interval
                for interval in working_intervals
                for sub_interval in self._leave_intervals(interval, leaves)]

        # adapt tz
        return [self._interval_new(
            self.string_to_datetime(interval[0]),
            self.string_to_datetime(interval[1]),
            interval[2]) for interval in working_intervals]

    
    def _get_day_attendances(self, day_date, start_time, end_time):
        """ Given a day date, return matching attendances. Those can be limited
        by starting and ending time objects. """
        self.ensure_one()
        weekday = day_date.weekday()
        attendances = self.env['resource.calendar.attendance']

        for attendance in self.attendance_ids.filtered(
            lambda att:
                int(att.dayofweek) == weekday and
                not (att.date_from and fields.Date.from_string(att.date_from) > day_date) and
                not (att.date_to and fields.Date.from_string(att.date_to) < day_date)):
            if start_time and self.float_to_time(attendance.hour_to) < start_time:
                continue
            if end_time and self.float_to_time(attendance.hour_from) > end_time:
                continue
            attendances |= attendance
        return attendances

    def _iter_day_attendance_intervals(self, day_date, start_time, end_time):
        """ Get an iterator of all interval of current day attendances. """
        for calendar_working_day in self._get_day_attendances(day_date, start_time, end_time):
            from_time = self.float_to_time(calendar_working_day.hour_from)
            to_time = self.float_to_time(calendar_working_day.hour_to)

            dt_f = datetime.datetime.combine(day_date, max(from_time, start_time))
            dt_t = datetime.datetime.combine(day_date, min(to_time, end_time))

            yield self._interval_new(dt_f, dt_t, {'attendances': calendar_working_day})



