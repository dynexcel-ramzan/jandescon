# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class HrRestDayGenerate(models.TransientModel):
    _name = 'hr.gazetted.day.generate'
    _desscription = 'Rest Day Wizard'

   
    shift_ids =fields.Many2many('resource.calendar', string="Shifts")
    gazetted_days_ids =fields.One2many('gazetted.day.generate.line', 'generate_id' , string="Rest Day")
    
    def action_schedule_gazetted_days(self):
        """Create mass schedule for all departments based on the Rest Day scheduled in corresponding employee's contract"""
        
        if self.shift_ids:
            for shift in self.shift_ids:                  
                for gazetted_day in self.gazetted_days_ids:                         
                    gazetted_day_ids = [(0, 0, {
                                            'name': gazetted_day.name,
                                            'date_from': gazetted_day.date_from,
                                            'date_to': gazetted_day.date_to,
                                            'work_entry_type_id': gazetted_day.work_entry_type_id.id, 

                                        })]
                    shift.global_leave_ids = gazetted_day_ids 








class RestDayGenerateLine(models.TransientModel):
    _name = 'gazetted.day.generate.line'
    _description =  'Gazetted Days Wizard Line'

    name = fields.Char(string="Name") 
    date_from = fields.Datetime(string="Date From",  help="Start date")
    date_to = fields.Datetime(string="Date To",  help="end date")
    work_entry_type_id = fields.Many2one('hr.work.entry.type', string="Entry Type",  help="entry type")
    generate_id = fields.Many2one('hr.gazetted.day.generate', string='Gazetted Generate', help="Company")
