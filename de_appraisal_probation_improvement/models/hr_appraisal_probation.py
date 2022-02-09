from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class HrAppraisalProbation(models.Model):
    _name = 'hr.appraisal.probation'
    _description = 'HR Appraisal Probation'
    
    @api.model
    def create(self, values):
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code('hr.appraisal.probation.name') or _('New')    
        return super(HrAppraisalProbation, self).create(values)
    
    name = fields.Char('Name', required=True, copy=False, readonly=True, index=True,
                          default=lambda self: _('New'))
    
    employee_id = fields.Many2one('hr.employee', string="Employee")
    grade = fields.Many2one('grade.type', related='employee_id.grade_type',string='Grade', )
    position = fields.Char(string='Position', related='employee_id.job_title')
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id')
    date_of_joining = fields.Date(string='Date of Joining',compute='compute_joining_date')
    expiry = fields.Date(string='Probation Expiry', compute='compute_confirm_date')
    target_Year = fields.Char(string='Target Year',default=datetime.now().year)
    # Managers Info
    manager_name = fields.Many2one('hr.employee', string='Name', related='employee_id.parent_id')
    designation = fields.Many2one('grade.designation', string='Designation',compute='compute_mngr_desig')
    #, related='employee_id.parent_id.grade_designation.id'
    # Areas of Review:
    reviewed_employee = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                         string='Have you reviewed the JD with employee?')
    # Evaluate employee’s performance with respect to:
    knowledge = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], string="Job Knowledge")
    productivity = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], string="Productivity")

    quality_of_work = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                       string="Quality of work/attention to details")
    technical_skills = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                        string="Technical skills")
    analytical_skills = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                         string="Analytical Skills")
    creativity = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], string="Creativity")
    team_player = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], string="Team Player")
    hardwork = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], string="Hard Work")
    communication_skills = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                            string="Communication Skills")
    dependability = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                     string="Dependability")
    initiative = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                  string="Initiative/Risk Taking")
    meet_deadline = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                     string="Meet Deadlines")
    discipline = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                  string="Discipline & Punctuality")
    overall_evaluation = fields.Float(string='Overall Evaluation', compute='compute_over_all_evaluation')
    #
    employee_can_excel = fields.Text('Are there any area(s) where the employee can excel? (Please Specify): ')
    improvement_is_required = fields.Text('Are there any area(s) where improvement is required? (Please Specify): ')
    # Confirmation Status
    confirmation_status = fields.Selection([('confirm','Confirm Employee'),('dont_confirm','Do Not Confirm')
                                            ,('extend','Extend Probation')],string = 'Status')

    gross_salary = fields.Integer('Gross Salary')  # Appears if "Confirm Employee?" is Checked
    grade = fields.Char('Grade')  # Manual Input #Appears if "Confirm Employee?" is Checked
    with_from = fields.Date('W.E.F')  # Appears if "Confirm Employee?" is Checked
    probation_extension_period = fields.Selection([('1', '1 Months'), ('3', '3 Months'), ('6', '6 Months')],
                                                  string='Probation extension Period')
    # HOD Comments
    comments = fields.Text('Comments')
    # Employee Comments
    employee_comment = fields.Text('Comments')
    # HR Comments
    hr_comments = fields.Text('HR Comments')
    state = fields.Selection([
        ('draft', 'Draft'),('confirmed', 'Confirmed'),
        ('employee_waiting', 'Sent For Employees Review'),
        ('employee_review', 'Reviewed By Employee'), ('hr_review', 'Reviewd By HR'), ('done', 'Done')], string='State', index=True,
         default='draft', track_visibility='onchange')

    
    def compute_joining_date(self):
        for rec in self:
            self.date_of_joining = rec.employee_id.date
    
    def compute_confirm_date(self):
        for rec in self:
            self.expiry = rec.employee_id.confirm_date
    
    def compute_over_all_evaluation(self):
        for rec in self:
            self.overall_evaluation = round(
                (int(rec.knowledge) + int(rec.productivity) + int(rec.quality_of_work) + int(
                    rec.technical_skills) + int(rec.analytical_skills) + int(rec.creativity) +
                 int(rec.team_player) + int(rec.hardwork) +
                 int(rec.communication_skills) + int(
                    rec.dependability) + int(rec.initiative) + int(rec.meet_deadline)
                 + int(rec.discipline)) / 13, 2)
            
    def action_confirmed(self):
        self.state='confirmed'
    
    def action_reset(self):
        if self.state == 'confirmed':
            self.state='draft'
        elif self.state == 'employee_waiting':
            self.state='confirmed'
        elif self.state == 'employee_review':
            self.state='employee_waiting'
        elif self.state == 'hr_review':
            self.state = 'employee_review'
        elif self.state == 'done':
            self.state = 'employee_review'
            
    def action_waiting(self):
        self.state = 'employee_waiting'
        
    def action_review(self):
        self.state = 'employee_review'
    
    def action_hr_review(self):
        self.state = 'hr_review'
    
    def action_done(self):
        self.state = 'done'
    
    def compute_mngr_desig(self):
        self.designation = self.employee_id.parent_id.grade_designation.id
        
    @api.constrains('reviewed_employee','knowledge','quality_of_work','technical_skills','analytical_skills',
                    'creativity','team_player','hardwork','communication_skills','dependability','initiative',
                   'meet_deadline','discipline')
    def constrains_performance(self):
        if not self.reviewed_employee and self.state !='draft':
            raise UserError('You should check! Have you reviewed the JD with employee?')
            
        if not self.knowledge and self.state !='draft':
            raise UserError("You Should Rate Job Knowledge")
        
        if not self.quality_of_work and self.state !='draft':
            raise UserError("You Should Rate Quality Of Work")
        
        if not self.technical_skills and self.state !='draft':
            raise UserError("You Should Rate Technical Skills")                            
        
        if not self.analytical_skills and self.state !='draft':
            raise UserError("You Should Rate Analaytical Skills")                            
        
        if not self.creativity and self.state !='draft':
            raise UserError("You Should Rate Creativity")                            
        
        if not self.team_player and self.state !='draft':
            raise UserError("You Should Rate Team Player")                            
        
        if not self.hardwork and self.state !='draft':
            raise UserError("You Should Rate Hardwork")                            
        
        if not self.communication_skills and self.state !='draft':
            raise UserError("You Should Rate Communication Skills")                            
        
        if not self.dependability and self.state !='draft':
            raise UserError("You Should Rate Dependability")                            
        
        if not self.initiative and self.state !='draft':
            raise UserError("You Should Rate Initiative")                            
        
        if not self.meet_deadline and self.state !='draft':
            raise UserError("You Should Rate Meet Deadlines")                            
        
        if not self.discipline and self.state !='draft':
            raise UserError("You Should Rate Discipline")


    def unlink(self):
        if self.state == 'draft':
            raise UserError(('A record not in draft state can`t be deleted!'))