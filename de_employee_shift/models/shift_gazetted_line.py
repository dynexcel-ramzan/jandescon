# -*- coding: utf-8 -*-
from odoo.exceptions import Warning
from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class ShiftGazettedLine(models.Model):
    _name = 'shift.gazetted.line'
    _description = 'Shift Gazetted Line'
    _rec_name = 'date'

    date = fields.Date(string='Date')
    shift_id = fields.Many2one('resource.calendar', string='Shift')


    
class ShiftGazetted(models.Model):
    _inherit = 'resource.calendar.leaves'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ShiftGazetted, self).create(vals_list)
        res.action_create_line()
        return res
    
    def write(self, vals_list):
        res = super(ShiftGazetted, self).write(vals_list)
        self.action_create_line()
        return res

    def action_create_line(self):
        for rec in self:
            date_range =  (rec.date_to - rec.date_from).days + 1
            for line in range(date_range):
                date_execute = (rec.date_from + relativedelta(hours=+5)) + timedelta(line) 
                exist_record =self.env['shift.gazetted.line'].search([('shift_id','=',rec.calendar_id.id),('date','=',date_execute)])
                if not exist_record:
                    vals = {
                        'date': date_execute,
                        'shift_id': rec.calendar_id.id,
                    }
                    gazetted_line = self.env['shift.gazetted.line'].create(vals)

    
class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'
    
    
    def action_create_line(self):
        for rec in self.global_leave_ids:
            date_range =  (rec.date_to - rec.date_from).days + 1
            for line in range(date_range):
                date_execute = (rec.date_from + relativedelta(hours=+5)) + timedelta(line) 
                exist_record =self.env['shift.gazetted.line'].search([('shift_id','=',rec.calendar_id.id),('date','=',date_execute)])
                if not exist_record:
                    vals = {
                        'date': date_execute,
                        'shift_id': rec.calendar_id.id,
                    }
                    gazetted_line = self.env['shift.gazetted.line'].create(vals)
