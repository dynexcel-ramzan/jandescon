from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrRecruitmentWizard(models.TransientModel):
    _name = "hr.recruitment.wizard"
    _description = "Recruitment Wizard"

    req_new_recruits = fields.Integer(string='Requested Number of new Recruits')
    appr_new_recruits = fields.Integer(string='Approved Number of new Recruits')
    request_id = fields.Many2one('hr.recruitment.request')
    job_id = fields.Many2one('hr.job')

    @api.onchange('req_new_recruits')
    def abc(self):
        model = self.env.context.get('active_model')
        rec = self.env[model].browse(self.env.context.get('active_id'))
        self.req_new_recruits = rec.people_recruit

    def action_done_head_count(self):
        if self.appr_new_recruits > self.req_new_recruits or self.appr_new_recruits < 0:
            raise UserError(_("Approved Recruits cannot be greater than Requested no. of Recruits!"))

        self.request_id.update({
            'head_count_non_budgeted': self.appr_new_recruits,
            'state' : 'approved'
        })
        
        self.job_id.update({
            'head_approved_count_unbug': self.job_id.head_approved_count_unbug + self.appr_new_recruits,
        })

