from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class EmployeeTraining(models.Model):
    _name = 'employee.training'
    _description = 'Employee training model'

    def unlink(self):
        for r in self:
            if r.state == 'done':
                raise UserError("EMP_Training records which are set to done can't be deleted!")
        return super(EmployeeTraining, self).unlink()

    @api.model
    def create(self, values):
        if values.get('emp_training', _('New')) == _('New'):
            values['emp_training'] = self.env['ir.sequence'].next_by_code('employee.training.emp_training') or _('New')
        return super(EmployeeTraining, self).create(values)

    crnt_year = fields.Integer(string="Current Year", default=datetime.now().year)
    emp_training = fields.Char('TRN/2021/00001', required=True, copy=False, readonly=True, index=True,
                               default=lambda self: _('New'))

    company_id = fields.Many2one('res.company', string="Company")

    name = fields.Char('Name', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    duration = fields.Char(string='Duration', compute='onchange_birthday')
    institute = fields.Char('Institute')
    course_name = fields.Char('Course Name')
    course_type = fields.Selection(
        [('short course', 'Short Course'), ('certification', 'Certification'), ('degree', 'Degree'),
         ('diploma', 'Diploma'),
         ('seminar', 'Seminar'), ('lab training', 'Lab Training'), ('workshop', 'Workshop')], string="Course Type")
    trainer_name = fields.Char('Trainer Name')
    venue = fields.Char('Venue')
    description = fields.Char('Description')
    amount = fields.Float('Amount')
    reason = fields.Char('Reason')

    # Venue Evaluation fields
    physical_arrangement = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                            string="Physical arrangements of the program")
    refreshment_arrangement = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                               string="Refreshment arrangement during program")
    accessibility_venue = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                           string="Accessibility to the venue")

    # training evaluation fields
    knowledge = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                 string="Knowledge")
    preparation = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                   string="Preparation")
    attitude_style_delivery = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                               string="Attitude Style Delivery")
    encouraged_participation = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                                string="Encouraged Participation")
    learning_atmosphere = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                           string="Learning Atmosphere")
    ability_handle_queries = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                              string="Ability Handle Queries")

    # evaluation fields:
    curriculum_content = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                          string="Curriculum content")
    relevance_job = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                     string="Relevance to your job")
    application_training_job = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                                string="Application of training to the job")
    length_of_the_program = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                             string="Length of the program")
    use_of_audio_visual_aids = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                                string="Use of audio/ visual aids")

    # Aggregate field:
    aggregate = fields.Char('Aggregate', compute='compute_aggregate')

    # Other info fields:
    recommend_course = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                        string="Would you recommend this course to other colleagues?")

    course_learning_applied = fields.Text(
        string="Things you learnt from the course that would be applied immediately to the job?")

    conduct_training_differently = fields.Text(
        string="If you were to conduct the training, what would you do differently?")

    delivery_date = fields.Date(string="When would you be ready to deliver this program internally?")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='State', index=True, copy=False, default='draft', track_visibility='onchange')

    @api.depends('physical_arrangement', 'refreshment_arrangement', 'accessibility_venue', 'knowledge',
                 'preparation',
                 'attitude_style_delivery', 'encouraged_participation', 'learning_atmosphere',
                 'ability_handle_queries',
                 'curriculum_content', 'relevance_job', 'application_training_job', 'length_of_the_program'
        , 'use_of_audio_visual_aids')
    @api.constrains('physical_arrangement', 'refreshment_arrangement', 'accessibility_venue', 'knowledge',
                    'preparation',
                    'attitude_style_delivery', 'encouraged_participation', 'learning_atmosphere',
                    'ability_handle_queries',
                    'curriculum_content', 'relevance_job', 'application_training_job', 'length_of_the_program'
        , 'use_of_audio_visual_aids')
    def constraints_on_selection(self):
        if not self.physical_arrangement:
            raise UserError("Please select a value in ""physical arrangement!"" ")
        if not self.refreshment_arrangement:
            raise UserError("Please select a value in ""refreshment arrangement!"" ")
        if not self.accessibility_venue:
            raise UserError("Please select a value in ""accessibility venue!"" ")
        if not self.knowledge:
            raise UserError("Please select a value in ""knowledge!"" ")
        if not self.preparation:
            raise UserError("Please select a value in ""preparation!"" ")
        if not self.attitude_style_delivery:
            raise UserError("Please select a value in ""attitude style delivery!"" ")
        if not self.encouraged_participation:
            raise UserError("Please select a value in ""encouraged participation!"" ")
        if not self.learning_atmosphere:
            raise UserError("Please select a value in ""learning atmosphere!"" ")
        if not self.ability_handle_queries:
            raise UserError("Please select a value in ""ability handle queries!"" ")
        if not self.curriculum_content:
            raise UserError("Please select a value in ""curriculum content!"" ")
        if not self.relevance_job:
            raise UserError("Please select a value in ""relevance job!"" ")
        if not self.application_training_job:
            raise UserError("Please select a value in ""application training job!"" ")
        if not self.length_of_the_program:
            raise UserError("Please select a value in ""length of the program..!"" ")
        if not self.use_of_audio_visual_aids:
            raise UserError("Please select a value in use of ""audio visual aids!"" ")

    def action_done(self):
        self.constraints_on_selection()
        self.state = 'done'

    def onchange_birthday(self):
        dob = self.date_from
        delta = self.date_to - self.date_from
        self.duration = str(delta.days)

    def compute_aggregate(self):
        for rec in self:
            rec.aggregate = round((int(rec.physical_arrangement) + int(rec.refreshment_arrangement)
                                   + int(rec.accessibility_venue) + int(rec.knowledge) + int(rec.preparation)
                                   + int(rec.attitude_style_delivery) + int(rec.encouraged_participation)
                                   + int(rec.learning_atmosphere) + int(rec.ability_handle_queries)
                                   + int(rec.curriculum_content) + int(rec.relevance_job)
                                   + int(rec.application_training_job) + int(rec.length_of_the_program)
                                   + int(rec.use_of_audio_visual_aids)) / 14, 2)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    def action_view_training_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': ('Training'),
            'res_model': 'employee.training',
            'view_mode': 'tree',
            'view_id': self.env.ref('de_employee_training.view_employee_training_tree', False).id,
            'domain': [('employee_id', '=', self.id)],
        }
