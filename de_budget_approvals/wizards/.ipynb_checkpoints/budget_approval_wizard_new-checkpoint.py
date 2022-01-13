from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrRecruitmentWizard(models.TransientModel):
    _name = "hr.recruitment.wizard.new"
    _description = "Recruitment Wizard"

    req_new_recruits = fields.Integer(string='Requested Number of new Recruits')
    appr_new_recruits = fields.Integer(string='Approved Number of new Recruits')

    @api.onchange('req_new_recruits')
    def abc(self):
        model = self.env.context.get('active_model')
        rec = self.env[model].browse(self.env.context.get('active_id'))
        self.req_new_recruits = rec.people_recruit

    def action_done_new_job(self):
        model = self.env.context.get('active_model')
        rec = self.env[model].browse(self.env.context.get('active_id'))
        if self.appr_new_recruits > self.req_new_recruits or self.appr_new_recruits < 0:
            raise UserError("Approved Recruits cannot be greater than Requested no. of Recruits!")

        rec.write({
            'head_count_un_budgeted': self.appr_new_recruits
        })

        record = self.env['hr.job'].create({
            'name': rec.job_title,
            'company_id': rec.company.id,
            'short_code': rec.short_code_new,
            'grade' : rec.grade_type,
            'head_approved_count_unbug' : rec.head_count_non_budgeted,

        })
        rec.state = 'approved'
