from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError


class EmployeeSession(models.Model):
    _name = 'employee.session'
    _description = 'Employee Session model'

    crnt_year = fields.Integer(string="Current Year", default=datetime.now().year)
    emp_seq = fields.Char('REQ/2021/00001', required=True, copy=False, readonly=True, index=True,
                          default=lambda self: _('New'))

    def unlink(self):
        for r in self:
            if r.state == 'done':
                raise UserError("EMP_Session records which are set to done can't be deleted!")
        return super(EmployeeSession, self).unlink()

    @api.model
    def create(self, values):
        if values.get('emp_seq', _('New')) == _('New'):
            values['emp_seq'] = self.env['ir.sequence'].next_by_code('employee.session.emp_seq') or _('New')
        return super(EmployeeSession, self).create(values)



    name = fields.Char('Name', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee ID', invisible=True)
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

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='State', index=True, copy=False, default='draft', track_visibility='onchange')
    employee_session_lines = fields.One2many('employee.session.line', 'session_id')

    participants_ids = fields.Many2many('hr.employee', string="Participants Id", reqiured=True)

    company_id = fields.Many2one('res.company', string="Company")

    @api.constrains('participants_ids')
    def constraints_on_selection(self):
        if not self.participants_ids:
            raise UserError("Please select atleast 1 Employee!")




    def action_done(self):
        flag=0
        for employee in self.participants_ids:
            print("**************", employee.id)
            vals = {
                'name': self.name,
                'course_name': self.course_name,
                'course_type': self.course_type,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'duration': self.duration,
                'institute': self.institute,
                'trainer_name': self.trainer_name,
                'venue': self.venue,
                'description': self.description,
                'amount': self.amount,
                'reason': self.reason,
                'employee_id':employee.id,
            }
            result = self.env['employee.training'].create(vals)
            flag=1

        if flag ==0:
            raise UserError("No participants added!")
        else:
            self.state = 'done'




    def onchange_birthday(self):
        dob = self.date_from
        delta = self.date_to - self.date_from
        self.duration = str(delta.days)

    # if dob:
    #     today = date.today()
    #     self.duration = str(today.day - dob.day - ((today.month, today.day) < (dob.month, dob.day))) + " Days"
    # else:
    #     self.duration = '-'

    #
    # for line in self:
    #     print(line.id)
    #     employee_training = self.env['employee.training'].create({
    #         'name': self.name,
    #         'course_name': self.course_name,
    #         'date_from': self.date_from,
    #         'date_to': self.date_to,
    #         'duration': self.duration,
    #         'institute': self.institute,
    #         'trainer_name': self.trainer_name,
    #         'venue': self.venue,
    #         'description': self.description,
    #         'amount': self.amount,
    #         'reason': self.reason
    #     })


class EmployeeSessionLine(models.Model):
    _name = 'employee.session.line'
    _description = 'Employee Session line'


    # name = fields.Many2one('hr.employee', string='Participants')
    session_id = fields.Many2one('employee.session')
