from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BudgetApproval(models.Model):
    _name = 'hr.recruitment.request'

    @api.model
    def create(self, values):
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code('hr.recruitment.request.name') or _('New')
        return super(BudgetApproval, self).create(values)

    name = fields.Char('Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))

    request_for = fields.Selection([('increase in head count', 'Increase in Head Count'),('new job position', 'New Job Position')],
        string='Request For', default='increase in head count')
    
    def action_approve(self):
        return {
            'name': ('Request Approval'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.recruitment.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_request_id': self.id,'default_job_id': self.job_position.id},
        }

    def unlink(self):
        for r in self:
            if r.state == 'approved' or r.state == 'refused':
                raise UserError("Hr-Recruitment records which are set to Approved/Refused can't be deleted!")
        return super(BudgetApproval, self).unlink()

    # Increase in Head Count fields( ihc )
    job_position = fields.Many2one('hr.job', string="Job Position")
    survey_id = fields.Many2one('hr.job', string="Survey ID")

    # sir Nasik Ap ny ye 2 fields ko edit krna hy
    # ================================
    head_count_budgeted = fields.Integer(related = 'job_position.head_approved_count_bug', string="Current Head Count(Budgeted)")
    head_count_non_budgeted = fields.Char(string="Approved Head Count(Non-Budgeted)")
    # ================================
    head_count_un_budgeted = fields.Integer(related = 'job_position.head_approved_count_unbug', string="Current Head Count(Un-Budgeted)")
    people_recruit = fields.Integer(string="Number of People to Recruit")
    reason = fields.Text(string="Reason")
    exp_compen = fields.Integer(string="Expected Compensation")
    qualification_req = fields.Selection(
        [('graduate', 'Graduate'), ('bachelor degree', 'Bachelor Degree'), ('masters degree', 'Masters Degree'),
         ('doctoral degree', 'Doctoral Degree')],
        string="Qualification Required")
    start_date = fields.Date(string="Desired Start Date")
    appr_num_new_recruit = fields.Integer(string="Approve Number of New Recruits")
    company = fields.Many2one('res.company', string="Company")
    job_title = fields.Text(string="Job Title")
    short_code_new = fields.Text(string="Short Code")
    grade_type = fields.Char(string="Grade")
    car_allowance  = fields.Selection([('yes', 'Yes'), ('no','No')], string="Car Allowance")
    mobile_allowance  = fields.Selection([('yes', 'Yes'), ('no','No')], string="Mobile Allowance")
    medical_allowance  = fields.Selection([('yes', 'Yes'), ('no','No')], string="Medical Allowance")
    other_allowance  = fields.Selection([('yes', 'Yes'), ('no','No')], string="Other Allowances")
    
    car_amount = fields.Integer(string="Car Allowance Amount")
    mobile_amount = fields.Integer(string="Mobile Allowance Amount")
    medical_amount = fields.Integer(string="Medical Allowance Amount")
    other_description = fields.Text(string="Other Allowances Description")
    other_amount = fields.Integer(string="Other Allowances Amount")
    
    is_check = fields.Boolean(string="Check", default=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
    ], string='State', index=True, copy=False, default='draft')

    @api.onchange('request_for')
    def is_check_field(self):
        if self.request_for == 'increase in head count':
            self.is_check = True
        else:
            self.is_check = False

    def action_submitted(self):
        self.state = 'submitted'

    def action_approved(self):
        self.state = 'approved'

    def action_refused(self):
        self.state = 'refused'

    number = fields.Integer(string="Number")
