from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError


class HrRequest(models.Model):
    _name = 'hr.request'
    _description = 'HR Request'

    @api.model
    def create(self, values):
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code('hr.request.name') or _('New')
        return super(HrRequest, self).create(values)

    name = fields.Char('Sequence', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    user_id = fields.Many2one(related='employee_id.user_id')
    
    grade = fields.Many2one('grade.type', related='employee_id.grade_type', string='Grade')
    position = fields.Char(string='Position', related='employee_id.job_title')
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id')
    date_of_joining = fields.Date(string='Date of Joining', compute='compute_joining_date')

    # Managers Info
    manager_name = fields.Many2one('hr.employee', string='Manager Name', related='employee_id.parent_id')
    designation = fields.Many2one('grade.designation', related='employee_id.parent_id.grade_designation', readonly="1")
    # , related='employee_id.parent_id.grade_designation.id'
    request_type_id = fields.Many2one('hr.request.config', 'Request Type', required=True, domain="['|',('company_id','=',company_id),('company_id','=',False)]")
    category = fields.Selection([('hr', 'HR'), ('management', 'Management'), ('operations', 'Operations'),
                                 ('security', 'Security'), ('technical', 'Technical'), ('it', 'IT'),
                                 ('marketing', 'Marketing'), ('accounts', 'Accounts'), ('others', 'Others')],
                                string='Category',
                                related='request_type_id.category')
    description = fields.Text('Description', required=True)
    best_before_date = fields.Date('Best Before')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    state = fields.Selection([
        ('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('refused', 'Refused')],
        string='State', index=True,
        copy=False, default='draft', track_visibility='onchange')

    def compute_joining_date(self):
        for rec in self:
            rec.date_of_joining = rec.employee_id.date

    def action_submit(self):
        self.state = 'submitted'

    def action_approved(self):
        self.state = 'approved'

    def action_refused(self):
        self.state = 'refused'

    def unlink(self):
        if self.state != 'draft':
            raise UserError('You cannot Delete record which is not in Draft state')

    # @api.onchange('manager_name')
    # def onchange_abc(self):
    #     print(self.employee_id.parent_id.grade_designation)