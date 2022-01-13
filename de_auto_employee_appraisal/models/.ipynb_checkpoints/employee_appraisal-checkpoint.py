# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime
import calendar
from datetime import date


class EmployeeAppraisal(models.Model):
    _name = 'auto.employee.appraisal'
    _description = 'Auto Employee Appraisal'  

    run_date = fields.Date(string="Run date")
    mid_year_date = fields.Date(string="Mid year Date", required=True)
    end_year_date = fields.Date(string="End year Date", required=True)
    target_year = fields.Selection([('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023')
                                   , ('2024', '2024'), ('2025', '2025'), ('2026', '2026'), ('2027', '2027')
                                   , ('2028', '2028'), ('2029', '2029'), ('2030', '2031'), ('2032', '2032')
                                   , ('2033', '2033'), ('2034', '2034'), ('2035', '2035'), ('2036', '2036')
                                   , ('2037', '2037'), ('2038', '2038'), ('2039', '2039'), ('2040', '2040')],
                               string="Target Year", required = "required")
    concerned_person_id = fields.Many2one('res.users',string="Concerned Person")
    
    
    @api.constrains('end_year_date','mid_year_date')
    def onchange_dates(self):
        if self.mid_year_date <= self.run_date:
            raise UserError("Mid Year Date Should be Greater Than Run Date")
            
        if self.end_year_date <= self.mid_year_date:
            raise UserError("End Date should be Greater Than Mid Year Date")
            
                    
            
                        
    def auto_appraisal_action(self):
        records = []
           
        for record in self.search([('run_date','=', datetime.date.today())]):
            records.append(record)
        self.create_auto_appraisal_record(records)
        
        
        
    def create_auto_appraisal_record(self, records):
        for record in records:
            
            employees = self.env['hr.employee'].search([])
        
            for employee in employees:
                appraisal_exists = self.env['hr.appraisal'].search([('employee_id','=', employee.id),
                                                                    ('appraisal_year','=', record.target_year)])
                
                if not appraisal_exists:
                    rec =  self.env['hr.appraisal'].create({
                        'employee_id': employee.id,
                        'manager_ids': employee.parent_id.id,
                        'job_id': employee.contract_id.job_id.id,
                        'appraisal_year': record.target_year,
                        'date_mid': record.mid_year_date,
                        'date_end': record.end_year_date,
                        'description': 'auto appraisal created for '+ str(employee.name),
                    })
                
                
                
                    appraisal_objectives = self.env['hr.appraisal.objective'].search([('employee_id', '=', employee.id),('objective_year','=',record.target_year)])

                    if not appraisal_objectives:
                        activity_type = self.env['mail.activity.type'].search([('name', '=', 'To Do')])
                        model_id =self.env['ir.model'].search([('model', '=', 'hr.appraisal')])
                        today = date.today()
                        vals = {

                            'res_model_id': model_id.id,
                            'res_id': rec.id,  # bill id
                            'activity_type_id': activity_type.id,
                            'summary': 'Over Due Bill Alert!',
                            'date_deadline': today,
                            'automated': True,
                            'user_id': record.concerned_person_id.id,
                            'previous_activity_type_id': False,
                            'note': str(employee.name)+'has no objective for year'+str(record.target_year)+ 'Please create objective record so the appraisal process can Start.' 
                        }
                        obj = self.env['mail.activity'].create(vals)
            
            
            
                      
                
                
#     def unlink(self):
#         raise UserError(('Deletion is not Allowed!'))
            
 