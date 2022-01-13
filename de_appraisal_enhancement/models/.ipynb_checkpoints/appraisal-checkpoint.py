from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime
from datetime import date, datetime, timedelta

class HrAppraisalInherit(models.Model):
    _inherit = 'hr.appraisal'
    
    appraisal_year = fields.Selection([('2020', 'FY 2020-21'), 
                                       ('2021', 'FY 2021-22'), 
                                       ('2022', 'FY 2022-22'), 
                                       ('2023', 'FY 2023-24'),
                                       ('2024', 'FY 2024-25'), 
                                       ('2025', 'FY 2025-26'), 
                                       ('2026', 'FY 2026-27'), 
                                       ('2027', 'FY 2027-28'),
                                       ('2028', 'FY 2028-29'), 
                                       ('2029', 'FY 2029-30'), 
                                       ('2030', 'FY 2030-31'),
                                       ('2031', 'FY 2031-32'),
                                       ('2032', 'FY 2032-33'),
                                       ('2033', 'FY 2033-34'), 
                                       ('2034', 'FY 2034-35'), 
                                       ('2035', 'FY 2035-36'), 
                                       ('2036', 'FY 2036-37'),
                                       ('2037', 'FY 2037-38'), 
                                       ('2038', 'FY 2038-39'), 
                                       ('2039', 'FY 2039-40'), 
                                       ('2040', 'FY 2040-41')],
                               string="Appraisal Year", required = "required")
    date_end = fields.Date('End year Review Date')
    date_mid = fields.Date('Mid year Review Date')
    description = fields.Char('Description')
    employee_objectives = fields.Char('Objectives')
    employee_feedback = fields.Char('Feedback')
    
    def action_done(self):
        self.state = 'done'
    
    def unlink(self):
    	for rec in self:
    		if rec.state in ['done']:
    			raise UserError(('Deletion is Not Allowed!'))
    		return super(HrAppraisalInherit, self).unlink()    
        
    
    @api.onchange('date_end')
    def check_end_date(self):
        if self.date_mid > self.date_end:
            raise UserError(('Mid Year Review Date Cannot Be Greater Than End Year Review Date'))

        
    @api.model
    def create(self,vals):
        if vals['appraisal_year']:
            appraisal_exists = self.search([('state', '!=', 'cancel'),('employee_id','=',vals['employee_id']),('appraisal_year','=',vals['appraisal_year'])])
            if appraisal_exists:
                raise UserError(('Appraisal Already Exist for Selected Year'))
        result = super(HrAppraisalInherit, self).create(vals)
        return result 
    

    def auto_appraisal_cron(self):
        for appraisal_record in self.search([('state', '=', 'pending')]):
                appraisal_record.create_appraisal_record_action()

    
    def create_appraisal_record_action(self):
        appraisals = []
        for appraisal in self.search([('state', '=', 'pending')]):
            appraisals.append(appraisal)
        self.create_appraisal_record(appraisals)
        
    def action_view_feedback_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': ('FeedBack'),
            'res_model': 'hr.appraisal.feedback',
            'view_mode': 'tree',
            'view_id': self.env.ref('de_appraisal_enhancement.view_hr_appraisal_feedback_tree', False).id,
            'domain': [('name', '=', self.employee_id.id),('performance_period', '=', self.appraisal_year)],
        }
    
    def action_view_objective_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': ('Objective'),
            'res_model': 'hr.appraisal.objective',
            'view_mode': 'tree',
            'view_id': self.env.ref('de_appraisal_enhancement.view_hr_appraisal_objective_tree', False).id,
            'domain': [('employee_id', '=', self.employee_id.id),('objective_year', '=', self.appraisal_year)],
        }
        
    
    def create_appraisal_record(self, appraisals):
        for record in appraisals:
            mid_start_date = self.date_mid
            mid_deadline_date = mid_start_date + timedelta(days=10)
            end_start_date = self.date_end
            end_deadline_date = end_start_date + timedelta(days=10)
            rec =  self.env['hr.appraisal.feedback'].create({
                'name': record.employee_id.id,
                'performance_period': record.appraisal_year,
                'mid_year_date': record.date_mid,
                'date_mid_deadline': mid_deadline_date,
                'end_year_date': record.date_end,
                'date_end_deadline': end_deadline_date,
            })

            objective_ids = self.env['hr.appraisal.objective'].search([('employee_id', '=',record.employee_id.id),('objective_year', '=',record.appraisal_year)])
            if objective_ids:
                rec.update({
                'training_need': objective_ids.traing_need,
                })
                if objective_ids.objective_lines:
                    for line in objective_ids.objective_lines:
                        self.env['hr.appraisal.feedback.objective.line'].create({
                            'objective': line.objective,
                            'obj_description': line.measuring_indicator,
                            'weightage': line.weightage,
                            'priority': line.priority,
                            'feedback_id': rec.id
                        })


            value_ids = self.env['hr.appraisal.values'].search([('company_id','=',record.company_id.id)], order='company_id asc',limit=1)
            if value_ids:
                if value_ids.values_lines:
                    for line in value_ids.values_lines:
                        self.env['hr.appraisal.feedback.values.line'].create({
                            'core_values': line.core_value,
                            'core_description': line.description,
                            'weightage': line.weightage,
                            'priority': line.priority,
                            'feedback_id': rec.id})
                        
            objective_appraisee_ids = self.env['hr.appraisal.objective'].search([('employee_id', '=',record.employee_id.id),('objective_year', '=',record.appraisal_year)])
            if objective_ids:
                if objective_ids.objective_lines:
                    for line in objective_ids.objective_lines:
                        self.env['hr.appraisal.feedback.objective.appraisee.line'].create({
                            'objective': line.objective,
                            'obj_description': line.measuring_indicator,
                            'weightage': line.weightage,
                            'priority': line.priority,
                            'feedback_id': rec.id
                        })
                        
            value_appraisee_ids = self.env['hr.appraisal.values'].search([('company_id','=',record.company_id.id)], order='company_id asc',limit=1)
            if value_ids:
                if value_ids.values_lines:
                    for line in value_ids.values_lines:
                        self.env['hr.appraisal.feedback.values.appraisee.line'].create({
                            'core_values': line.core_value,
                            'core_description': line.description,
                            'weightage': line.weightage,
                            'priority': line.priority,
                            'feedback_id': rec.id
                        })
                        
                        
