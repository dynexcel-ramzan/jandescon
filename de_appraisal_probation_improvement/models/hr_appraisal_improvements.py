from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class HrAppraisalImprovements(models.Model):
    _name = 'hr.appraisal.improvements'
    _description = 'HR Appraisal Improvement'

    @api.model
    def create(self, values):
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code('hr.appraisal.improvements.name') or _('New')    
        return super(HrAppraisalImprovements, self).create(values)
    
    name = fields.Char('Name', required=True, copy=False, readonly=True, index=True,
                          default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string="Employee")
    grade = fields.Many2one('grade.type',string='Grade',compute='compute_grade_type')
    position = fields.Char(string='Position', related='employee_id.job_title')
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id')
    date_of_joining = fields.Date(string='Date of Joining', compute='compute_joining_date')
    # Managers Info
    manager_name = fields.Many2one('hr.employee', string='Name', related='employee_id.parent_id')
    designation = fields.Many2one('grade.designation', string='Designation')
     #RIP Info
    rating_scale = fields.Text(string = 'Rating Scale'
                               ,default="5 = Outstanding  4 = Exceeded Expectations  3 = Met Expectations   2 = Partially Met Expectations  1 = Needs  ")

    follow_up_period = fields.Selection([('1', '1 Months'), ('2', '2 Months'), ('3', '3 Months')],
                                                  string='Follow Up Period')
    follow_up_date = fields.Date(string='Follow Up Date', compute='compute_follow_up_date')
    
    appraisal_improve_line = fields.One2many('hr.appraisal.improvements.line','hr_aprsl_improve_id') #Connect line model
    state = fields.Selection([
        ('draft', 'Draft'),('confirmed', 'Confirmed'),
        ('employee_waiting', 'Waiting For Employee`s Review'),
        ('employee_review', 'Reviewed By Employee'), ('follow_up', 'Awaiting Follow Up'),
        ('done', 'Done')], string='State', index=True,
        copy=False, default='draft', track_visibility='onchange')
    employee_undertake_action =fields.Selection([('yes','Yes'),('no','No')]
                                               ,string="Did the Employee undertake corrective action?")
    ratings = fields.Float(string='Rating', compute='compute_all_ratings_line')
    comments = fields.Text(string='Comments')

    def compute_joining_date(self):
        for rec in self:
            self.date_of_joining = rec.employee_id.date
    
    def action_confirmed(self):
        self.state='confirmed'
            
    def action_waiting(self):
        self.state = 'employee_waiting'
        
    def action_review(self):
        self.state = 'employee_review'
    
    def action_follow_up(self):
        self.state = 'follow_up'
    
    def action_done(self):
        self.state = 'done'
    
    
    def compute_all_ratings_line(self):
        sum=0
        i=0
        if self.appraisal_improve_line:
            for rec in self.appraisal_improve_line:
                i=i+1
                sum = sum + rec.rating
        if i==0:
            self.ratings=0
        else:
            self.ratings = round((sum/i),2)
            
    def compute_grade_type(self):
        for rec in self:
            self.grade = rec.employee_id.grade_type.id
    
    def compute_follow_up_date(self):
        if self.follow_up_period:
            period=int(self.follow_up_period)
            self.follow_up_date = self.create_date + relativedelta(months=period)
        else:
            self.follow_up_date = False
        
        
class HrAppraisalImprovementsLine(models.Model):
    _name = 'hr.appraisal.improvements.line'
    _description = 'HR Appraisal Improvement Line'
    
    
    hr_aprsl_improve_id = fields.Many2one('hr.appraisal.improvements') #parent Model Connect ID
    performance_improvement_area = fields.Text('Performance Improvement Area')
    action_plan = fields.Text('Action Plan & Timeline')
    rating = fields.Selection([
        ('Outstanding Performance', 'Outstanding Performance'),
        ('Excellent Performance', 'Excellent Performance'),
        ('Strong Performance', 'Strong Performance'),
        ('Needs Improvement', 'Needs Improvement'),
        ('Unsatisfactory', 'Unsatisfactory'),
    ], string='Employee Rating Level', index=True, copy=False,)
    state = fields.Selection([
        ('draft', 'Draft'),('confirmed', 'Confirmed'),
        ('employee_waiting', 'Waiting For Employees Review'),
        ('employee_review', 'Reviewed By Employee'), ('hr_review', 'Reviewd By HR'),
            ('done', 'Done')], string='State', index=True,
         default='draft', related='hr_aprsl_improve_id.state')
    
    @api.model
    def create(self, vals):
        result = super(HrAppraisalImprovementsLine, self).create(vals)
        return result
    
    @api.model
    def write(self, vals):
        result = super(HrAppraisalImprovementsLine, self).write(vals)
        return result
    
   