# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api, _
# from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError, Warning, ValidationError


class RecruitmentEnhancement(models.Model):
    _inherit = 'hr.job'

    _sql_constraints = [('short_code_uniq', 'unique (short_code)', "Short Code Already Exists!"), ]

    position_type = fields.Selection([
        ('budget', 'Budgeted'),
        ('non_budget', 'Non Budget'),
        ], string='Position Type', index =True, copy=False, default='budget', track_visibility='onchange')
    grade = fields.Char('Grade')
    position_code = fields.Char('Position Code')
    head_approved_count_bug = fields.Integer()
    head_approved_count_unbug = fields.Integer()
    short_code =fields.Char('Short Code', size=5)

    is_head_count_readonly = fields.Boolean('Is Head Count?', compute='compute_head_count')
    no_of_recruitment = fields.Integer('Expected New Employees', compute='compute_new_employees')

    # def write(self, vals):
    #     print("Hello")
    #     code = self.env['hr.job'].search([('short_code', '=', self.short_code)])
    #     print(code)
    #     raise ValidationError(_("Short Code Already Exists"))
    #     rec = super(RecruitmentEnhancement, self).write(vals)

    # @api.constrains('short_code')
    # def compute_short_code(self):
    #     # if self.short_code:
    #     print(self.short_code)
    #     code = self.env['hr.job'].search([('short_code', '=', self.short_code)])
    #     for rec in code:
    #         print(rec.short_code)
    #     print(code)
    #     if code:
    #         raise ValidationError(_("Short Code Already Exists"))
    #     else:
    #         pass

    def compute_new_employees(self):
        for rec in self:
            rec.no_of_recruitment = (rec.head_approved_count_bug + rec.head_approved_count_unbug) - rec.no_of_employee

    def compute_head_count(self):
        record = self.env['res.groups'].search([('name', '=', 'Allow to Change Head Count Approved')])
        rec = self.env.user.id in record.users.ids
        if rec:
            data = True
        else:
            data = False
        self.is_head_count_readonly = data

    survey_id_1 = fields.Many2one('survey.survey')
    survey_id_2 = fields.Many2one('survey.survey')
    survey_id_3 = fields.Many2one('survey.survey')
    survey_id_4 = fields.Many2one('survey.survey')
    survey_id_5 = fields.Many2one('survey.survey')

    partner_id_a = fields.Many2one('res.users')
    partner_id_b = fields.Many2one('res.users')
    partner_id_c = fields.Many2one('res.users')
    partner_id_d = fields.Many2one('res.users')
    partner_id_e = fields.Many2one('res.users')
    interview_count = fields.Integer('No of Interviews')

    survey_bool_a = fields.Boolean(default=False)
    survey_bool_b = fields.Boolean(default=False)
    survey_bool_c = fields.Boolean(default=False)
    survey_bool_d = fields.Boolean(default=False)
    survey_bool_e = fields.Boolean(default=False)

    test_count = fields.Integer('No of Tests')
    test_id_1 = fields.Many2one('survey.survey')
    test_id_2 = fields.Many2one('survey.survey')
    test_id_3 = fields.Many2one('survey.survey')

    test_bool_a = fields.Boolean(default=False)
    test_bool_b = fields.Boolean(default=False)
    test_bool_c = fields.Boolean(default=False)

    @api.onchange('test_count')
    def compute_test_bools(self):
        if self.test_count == 0:
            self.test_bool_a = False
            self.test_bool_b = False
            self.test_bool_c = False
        elif self.test_count == 1:
            self.test_bool_a = True
            self.test_bool_b = False
            self.test_bool_c = False
        elif self.test_count == 2:
            self.test_bool_a = True
            self.test_bool_b = True
            self.test_bool_c = False
        elif self.test_count == 3:
            self.test_bool_a = True
            self.test_bool_b = True
            self.test_bool_c = True
        else:
            pass

    @api.onchange('test_count')
    def check_test_count(self):
        if self.test_count > 3:
            raise UserError('Number of Tests should be between 1-3')

    @api.onchange('interview_count')
    def check_inetrview_count(self):
        if self.interview_count > 5:
            raise UserError('Number of interviews should be between 1-5')

    @api.onchange('interview_count')
    def compute_survey_bools(self):
        if self.interview_count == 0:
            self.survey_bool_a = False
            self.survey_bool_b = False
            self.survey_bool_c = False
            self.survey_bool_d = False
            self.survey_bool_e = False
        elif self.interview_count == 1:
            self.survey_bool_a = True
            self.survey_bool_b = False
            self.survey_bool_c = False
            self.survey_bool_d = False
            self.survey_bool_e = False
        elif self.interview_count == 2:
            self.survey_bool_a = True
            self.survey_bool_b = True
            self.survey_bool_c = False
            self.survey_bool_d = False
            self.survey_bool_e = False
        elif self.interview_count == 3:
            self.survey_bool_a = True
            self.survey_bool_b = True
            self.survey_bool_c = True
            self.survey_bool_d = False
            self.survey_bool_e = False
        elif self.interview_count == 4:
            self.survey_bool_a = True
            self.survey_bool_b = True
            self.survey_bool_c = True
            self.survey_bool_d = True
            self.survey_bool_e = False
        elif self.interview_count == 5:
            self.survey_bool_a = True
            self.survey_bool_b = True
            self.survey_bool_c = True
            self.survey_bool_d = True
            self.survey_bool_e = True
        else:
            pass


class RecruitmentApplicationEnhancement(models.Model):
    _inherit = 'hr.applicant'

    name = fields.Char(required=False, readonly=1)
    cnic = fields.Char('CNIC', size=13)
    age = fields.Char('Age')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ], string='Gender', index =True, copy=False, default='', track_visibility='onchange')
    experience = fields.Char('Relevant Experience')
    interviews_count = fields.Integer(compute='compute_interview_count')
    assessment_count = fields.Integer(compute='compute_assessment_count')
    is_show_employee_button = fields.Boolean('Is Show Employee Button?', compute='compute_show_create_button')
    is_medical_certficate_sub = fields.Boolean(default=False)
    show_quick_promt = fields.Boolean(default=False, compute='compute_quick_prompt')

    def compute_quick_prompt(self):
        if self.cnic:
            employee_cnic = self.env['hr.employee'].search([('cnic', '=', self.cnic)])
            if employee_cnic:
                self.show_quick_promt = True
            else:
                self.show_quick_promt = False

    def compute_get_stages(self):
        if self.job_id:
            stages_list =[]
            stages_list.append(self.job_id.id)
            if self.job_id.interview_count == 1:
                stage = self.env['hr.recruitment.stage'].search([('name', '=', 'First Interview')])
                stage.write({'job_ids': stages_list})

            elif self.job_id.interview_count == 2:
                stage_1 = self.env['hr.recruitment.stage'].search([('name', '=', 'First Interview')])
                stage_2 = self.env['hr.recruitment.stage'].search([('name', '=', 'Second Interview')])
                stage_1.write({'job_ids': stages_list})
                stage_2.write({'job_ids': stages_list})

            elif self.job_id.interview_count == 3:
                stage_1 = self.env['hr.recruitment.stage'].search([('name', '=', 'First Interview')])
                stage_2 = self.env['hr.recruitment.stage'].search([('name', '=', 'Second Interview')])
                stage_3 = self.env['hr.recruitment.stage'].search([('name', '=', 'Third Interview')])
                stage_1.write({'job_ids': stages_list})
                stage_2.write({'job_ids': stages_list})
                stage_3.write({'job_ids': stages_list})

            elif self.job_id.interview_count == 4:
                stage_1 = self.env['hr.recruitment.stage'].search([('name', '=', 'First Interview')])
                stage_2 = self.env['hr.recruitment.stage'].search([('name', '=', 'Second Interview')])
                stage_3 = self.env['hr.recruitment.stage'].search([('name', '=', 'Third Interview')])
                stage_4 = self.env['hr.recruitment.stage'].search([('name', '=', 'Fourth Interview')])
                stage_1.write({'job_ids': stages_list})
                stage_2.write({'job_ids': stages_list})
                stage_3.write({'job_ids': stages_list})
                stage_4.write({'job_ids': stages_list})

            elif self.job_id.interview_count == 5:
                stage_1 = self.env['hr.recruitment.stage'].search([('name', '=', 'First Interview')])
                stage_2 = self.env['hr.recruitment.stage'].search([('name', '=', 'Second Interview')])
                stage_3 = self.env['hr.recruitment.stage'].search([('name', '=', 'Third Interview')])
                stage_4 = self.env['hr.recruitment.stage'].search([('name', '=', 'Fourth Interview')])
                stage_5 = self.env['hr.recruitment.stage'].search([('name', '=', 'Fifth Interview')])
                stages_list.append(stage_1.id)
                stages_list.append(stage_2.id)
                stages_list.append(stage_3.id)
                stages_list.append(stage_4.id)
                stages_list.append(stage_5.id)
                stage_1.write({'job_ids': stages_list})
                stage_2.write({'job_ids': stages_list})
                stage_3.write({'job_ids': stages_list})
                stage_4.write({'job_ids': stages_list})
                stage_5.write({'job_ids': stages_list})

            if self.job_id.test_count == 1:
                stage_1 = self.env['hr.recruitment.stage'].search([('name', '=', 'First Test')])
                stages_list.append(stage_1.id)
                stage_1.write({'job_ids': stages_list})

            elif self.job_id.test_count == 2:
                stage_1 = self.env['hr.recruitment.stage'].search([('name', '=', 'First Test')])
                stage_2 = self.env['hr.recruitment.stage'].search([('name', '=', 'Second Test')])
                stages_list.append(stage_1.id)
                stages_list.append(stage_2.id)
                stage_1.write({'job_ids': stages_list})
                stage_2.write({'job_ids': stages_list})

            elif self.job_id.test_count == 3:
                stage_1 = self.env['hr.recruitment.stage'].search([('name', '=', 'First Test')])
                stage_2 = self.env['hr.recruitment.stage'].search([('name', '=', 'Second Test')])
                stage_3 = self.env['hr.recruitment.stage'].search([('name', '=', 'Third Test')])
                stages_list.append(stage_1.id)
                stages_list.append(stage_2.id)
                stages_list.append(stage_3.id)
                stage_1.write({'job_ids': stages_list})
                stage_2.write({'job_ids': stages_list})
                stage_3.write({'job_ids': stages_list})

    stage_id = fields.Many2one('hr.recruitment.stage',  compute='compute_get_stages')

    def compute_show_create_button(self):
        self.is_show_employee_button = self.stage_id.is_show_employee_button

    def compute_interview_count(self):
        rec = self.env['hr.recruitment.interviews'].search_count([('applicant_id', '=', self.id)])
        self.interviews_count = rec

    def compute_assessment_count(self):
        rec = self.env['hr.recruitment.assessment'].search_count([('applicant_id', '=', self.id)])
        self.assessment_count = rec

    def action_next_stage(self):
        if self.stage_id:
            stage_list = []
            stages = self.env['hr.recruitment.stage'].search(['|',('job_ids', '=', self.job_id.id), ('is_non_fixed_stage', '=', False)])
            for stage in stages:
                stage_list.append(stage.id)
            if self.stage_id.id in stage_list:
                current_stage = self.stage_id.id
                if current_stage != stage_list[-1]:
                    state = self.env['hr.recruitment.stage'].browse([current_stage])
                    if state.name != 'Medical Clearance':
                        stage_index = stage_list.index(current_stage)
                        next_stage = stage_list[stage_index+1]
                        next = self.env['hr.recruitment.stage'].browse([next_stage])
                        self.stage_id = next.id
                    else:
                        if self.is_medical_certficate_sub:
                            stage_index = stage_list.index(current_stage)
                            next_stage = stage_list[stage_index + 1]
                            next = self.env['hr.recruitment.stage'].browse([next_stage])
                            self.stage_id = next.id
                        else:
                            raise UserError("Please Submit Medical Certificate!!!!")
                else:
                    pass

    def action_open_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Warning',
            'view_id': self.env.ref('de_recruitment_enhancement.view_recruitment_warning_wizard_form', False).id,
            'target': 'new',
            'res_model': 'warning.wizard',
            'view_mode': 'form',
        }

    @api.constrains('cnic')
    def compute_cnic(self):
        if self.cnic:
            if len(self.cnic) < 13:
                self.action_open_wizard()
                raise UserError('Invalid CNIC')
            if not self.cnic.isdigit():
                raise UserError(('CNIC Number is invalid'))

    def action_recruitment_survey(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Recruitment Survey',
            'view_id': self.env.ref('de_recruitment_enhancement.view_recruitment_interview_tree', False).id,
            'target': 'current',
            'domain': [('applicant_id', '=', self.id)],
            'res_model': 'hr.recruitment.interviews',
            'views': [[False, 'tree']],
        }

    def action_recruitment_survey_assessment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Recruitment Assessment',
            'view_id': self.env.ref('de_recruitment_enhancement.view_recruitment_assessment_tree', False).id,
            'target': 'current',
            'domain': [('applicant_id', '=', self.id)],
            'res_model': 'hr.recruitment.assessment',
            'views': [[False, 'tree']],
        }

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.applicant.sequence') or _('New')
        now = datetime.datetime.now()
        job = self.env['hr.job'].browse([vals['job_id']])
        if job.short_code:
            vals['name'] = job.short_code+vals['name']
            rec = super(RecruitmentApplicationEnhancement, self).create(vals)
            if rec.job_id.interview_count == 1:
                rec.env['hr.recruitment.interviews'].create({
                    'interviewer_id': rec.job_id.partner_id_a.id,
                    'survey_id': rec.job_id.survey_id_1.id,
                    'applicant_id': rec.id,
                })
            elif rec.job_id.interview_count == 2:
                rec.env['hr.recruitment.interviews'].create({
                    'interviewer_id': rec.job_id.partner_id_a.id,
                    'survey_id': rec.job_id.survey_id_1.id,
                    'applicant_id': rec.id,
                })
                rec.env['hr.recruitment.interviews'].create({
                    'interviewer_id': rec.job_id.partner_id_b.id,
                    'survey_id': rec.job_id.survey_id_2.id,
                    'applicant_id': rec.id,
                })
            elif rec.job_id.interview_count == 3:
                rec.env['hr.recruitment.interviews'].create({
                    'interviewer_id': rec.job_id.partner_id_a.id,
                    'survey_id': rec.job_id.survey_id_1.id,
                    'applicant_id': rec.id,
                })
                rec.env['hr.recruitment.interviews'].create({
                    'interviewer_id': rec.job_id.partner_id_b.id,
                    'survey_id': rec.job_id.survey_id_2.id,
                    'applicant_id': rec.id,
                })
                rec.env['hr.recruitment.interviews'].create({
                    'interviewer_id': rec.job_id.partner_id_c.id,
                    'survey_id': rec.job_id.survey_id_3.id,
                    'applicant_id': rec.id,
                })
            elif rec.job_id.interview_count == 4:
                rec.env['hr.recruitment.interviews'].create({
                    'interviewer_id': rec.job_id.partner_id_a.id,
                    'survey_id': rec.job_id.survey_id_1.id,
                    'applicant_id': rec.id,
                })
                rec.env['hr.recruitment.interviews'].create({
                    'interviewer_id': rec.job_id.partner_id_b.id,
                    'survey_id': rec.job_id.survey_id_2.id,
                    'applicant_id': rec.id,
                })
                rec.env['hr.recruitment.interviews'].create({
                    'interviewer_id': rec.job_id.partner_id_c.id,
                    'survey_id': rec.job_id.survey_id_3.id,
                    'applicant_id': rec.id,
                })
                rec.env['hr.recruitment.interviews'].create({
                    'interviewer_id': rec.job_id.partner_id_d.id,
                    'survey_id': rec.job_id.survey_id_4.id,
                    'applicant_id': rec.id,
                })
            elif rec.job_id.interview_count == 5:
                rec.env['hr.recruitment.interviews'].create({
                    'interviewer_id': rec.job_id.partner_id_a.id,
                    'survey_id': rec.job_id.survey_id_1.id,
                    'applicant_id': rec.id,
                })
                rec.env['hr.recruitment.interviews'].create({
                    'assessment_date': datetime.datetime.today(),
                    'interviewer_id': rec.job_id.partner_id_b.id,
                    'survey_id': rec.job_id.survey_id_2.id,
                    'applicant_id': rec.id,
                })
                rec.env['hr.recruitment.interviews'].create({
                    'survey_id': rec.job_id.survey_id_3.id,
                    'interviewer_id': rec.job_id.partner_id_c.id,
                    'applicant_id': rec.id,
                })
                rec.env['hr.recruitment.interviews'].create({
                    'interviewer_id': rec.job_id.partner_id_d.id,
                    'survey_id': rec.job_id.survey_id_4.id,
                    'applicant_id': rec.id,
                })
                rec.env['hr.recruitment.interviews'].create({
                    'interviewer_id': rec.job_id.partner_id_e.id,
                    'survey_id': rec.job_id.survey_id_5.id,
                    'applicant_id': rec.id,
                })
            if rec.job_id.test_count == 1:
                rec.env['hr.recruitment.assessment'].create({
                    'survey_id': rec.job_id.test_id_1.id,
                    'applicant_id': rec.id,
                })
            elif rec.job_id.test_count == 2:
                rec.env['hr.recruitment.assessment'].create({
                    'survey_id': rec.job_id.test_id_1.id,
                    'applicant_id': rec.id,
                })
                rec.env['hr.recruitment.assessment'].create({

                    'survey_id': rec.job_id.test_id_2.id,
                    'applicant_id': rec.id,
                })
            elif rec.job_id.test_count == 3:
                rec.env['hr.recruitment.assessment'].create({
                    'survey_id': rec.job_id.test_id_1.id,
                    'applicant_id': rec.id,
                })
                rec.env['hr.recruitment.assessment'].create({
                    'survey_id': rec.job_id.test_id_2.id,
                    'applicant_id': rec.id,
                })
                rec.env['hr.recruitment.assessment'].create({
                    'survey_id': rec.job_id.test_id_3.id,
                    'applicant_id': rec.id,
                })
            return rec
        else:
            raise UserError('Please Short Code for the concerned jo position!')


    def create_assessment_tests(self):
        if self.job_id.test_count == 1:
            self.env['hr.recruitment.assessment'].create({
                'survey_id': self.job_id.test_id_1.id,
                'applicant_id': self.id.origin,
            })
        elif self.job_id.test_count == 2:
            self.env['hr.recruitment.assessment'].create({
                'survey_id': self.job_id.test_id_1.id,
                'applicant_id': self.id.origin,
            })
            self.env['hr.recruitment.assessment'].create({
                'survey_id': self.job_id.test_id_2.id,
                'applicant_id': self.id.origin,
            })
        elif self.job_id.test_count == 3:
            self.env['hr.recruitment.assessment'].create({
                'survey_id': self.job_id.test_id_1.id,
                'applicant_id': self.id.origin,
            })
            self.env['hr.recruitment.assessment'].create({
                'survey_id': self.job_id.test_id_2.id,
                'applicant_id': self.id.origin,
            })
            self.env['hr.recruitment.assessment'].create({
                'survey_id': self.job_id.test_id_3.id,
                'applicant_id': self.id.origin,
            })

class RefuseReasonInh(models.TransientModel):
    _inherit = 'applicant.get.refuse.reason'

    def action_refuse_reason_apply(self):
        model = self.env.context.get('active_model')
        rec = self.env[model].browse(self.env.context.get('active_id'))
        refuse_stage = self.env['hr.recruitment.stage'].search([('name', '=', 'Refused')])
        rec.stage_id = refuse_stage.id
        record = super(RefuseReasonInh, self).action_refuse_reason_apply()