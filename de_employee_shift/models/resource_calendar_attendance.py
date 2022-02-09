# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, _, tools
from datetime import datetime, time
import datetime
import math
from pytz import utc
from odoo.tools.float_utils import float_round
from collections import namedtuple


class ResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'
    
    day_period = fields.Selection([('morning', 'Morning'), ('afternoon', 'Afternoon'), ('night', 'Night')], required=True, default='morning')


    @api.onchange('hour_from', 'hour_to')
    def _onchange_hours(self):
        # avoid negative or after midnight
        self.hour_from = min(self.hour_from, 23.99)
        self.hour_from = max(self.hour_from, 0.0)
        self.hour_to = min(self.hour_to, 23.99)
        self.hour_to = max(self.hour_to, 0.0)

        # avoid wrong order
#         self.hour_to = max(self.hour_to, self.hour_from)
