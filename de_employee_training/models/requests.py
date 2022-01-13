from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, timedelta,datetime


class EmployeeRequest(models.Model):
    _name = 'employee.request'
    _description = 'Employee Request model'

    def unlink(self):
        for r in self:
            if r.state == 'approved' or r.state == 'refused' or r.state == 'in session':
                raise UserError("EMP_Request records which are set to Approved/Refused/InSession can't be deleted!")
        return super(EmployeeRequest, self).unlink()

    @api.model
    def create(self, values):
        if values.get('emp_req', _('New')) == _('New'):
            values['emp_req'] = self.env['ir.sequence'].next_by_code('employee.request.emp_req') or _('New')
        return super(EmployeeRequest, self).create(values)

    crnt_year = fields.Integer(string="Current Year", default= datetime.now().year)
    emp_req = fields.Char('REQ/2021/00001', required=True, copy=False, readonly=True, index=True,
                          default=lambda self: _('New'))

    name = fields.Char(string='Name', required=True)
    reason = fields.Text(string='Reason', required=True)

    hr_remarks = fields.Text(string="HR Remarks")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('in session', 'In Session'),
        ('refused', 'Refused')
    ], string='State', index=True, copy=False, default='draft', track_visibility='onchange')

    employee_request_lines = fields.One2many('employee.request.line', 'request_id')

    participants_ids = fields.Many2many('hr.employee', string="Participants Id", reqiured=True)

    company_id = fields.Many2one('res.company', string="Company")

    @api.constrains('participants_ids')
    def constraints_on_selection(self):
        if not self.participants_ids:
            raise UserError("Please select atleast 1 Employee!")




    # employee_training_lines = fields.One2many('employee.training.line', 'request_id')

    def action_approved(self):
        self.state = 'approved'

    def action_submitted(self):
        flag = 0
        for rec in self.participants_ids:
            flag = 1
        if flag == 0:
            raise UserError("No participants added!")
        else:
            self.state = 'submitted'

    def action_refused(self):
        self.state = 'refused'

    def send_to_session(self):
        vals = {
            'name': self.name,
            'course_name': self.course,
            'institute': self.institute,
            'reason': self.reason,
            'participants_ids': self.participants_ids,
            'date_from': self.current_date,
            'date_to': self.end_date,
            'amount':self.training_cost
        }

        result = self.env['employee.session'].create(vals)
        self.state = 'in session'



    current_date = date.today()
    end_date = current_date + timedelta(days=30)
    course = fields.Char('Course')
    institute = fields.Char('Institute')
    training_date = fields.Date('Training Date')
    training_cost = fields.Integer('Training Cost')
    areas_of_improve = fields.Text(string="Target Areas of Improvement")


class EmployeeRequestLine(models.Model):
    _name = 'employee.request.line'
    _description = 'employee Request model'

    name = fields.Many2one('hr.employee', string='Participants', required=True)
    request_id = fields.Many2one('employee.request')

    # emp_number = fields.Char('Employee Number', related='name.contract_id.job_id.name')
    designation = fields.Char('Designation', related='name.contract_id.job_id.name')
    department = fields.Char('Department', related='name.department_id.name')
    # date_of_joining = fields.Date('Date of joining')
    # position = fields.Char('Position')

# class EmployeeTrainingLine(models.Model):
#     _name = 'employee.training.line'
#     _description = 'employee Request model'
#
#
#
#     request_id = fields.Many2one('employee.request')
