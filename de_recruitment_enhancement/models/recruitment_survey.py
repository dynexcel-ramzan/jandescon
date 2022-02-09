# -*- coding: utf-8 -*-

from odoo import models, fields, api
import uuid
from datetime import datetime
import werkzeug
from odoo.exceptions import UserError

class RecruitmentEnhancementAssessment(models.Model):
    _name = 'hr.recruitment.assessment'

    def _get_default_access_token(self):
        return str(uuid.uuid4())

    attempt_date = fields.Date('Attempt Date')
    # interviewer_id = fields.Many2one('res.users')
    performed_by_id = fields.Many2one('res.partner')
    performed_by = fields.Many2one('hr.applicant')
    applicant_id = fields.Many2one('hr.applicant')
    survey_id = fields.Many2one('survey.survey')
    score_percentage =fields.Float('Score Percentage')
    score_total =fields.Float('Total Score')
    response_id = fields.Many2one('survey.user_input', "Response", ondelete="set null")
    access_token = fields.Char('Access Token', default=lambda self: self._get_default_access_token(), copy=False)

    def action_invite_participant(self):
        if self.applicant_id.email_from:
            template_id = self.env.ref('de_recruitment_enhancement.mail_template_user_input_invite_survey').id
            template = self.env['mail.template'].browse(template_id)
            template.send_mail(self.id, force_send=True)
        else:
            raise UserError('Applicant Email is Empty')

    def action_print_answers(self):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        self.ensure_one()
        return self.survey_id.action_print_survey(answer=self.response_id)

    def action_start_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if not self.response_id:
            response = self.survey_id._create_answer(partner=self.performed_by_id)
            print(response)
            self.response_id = response.id
        else:
            response = self.response_id
        # grab the token of the response and start surveying
        self.performed_by = self.applicant_id
        self.score_percentage = response.scoring_percentage
        self.score_total = response.scoring_total
        self.performed_by_id = self.env.user.id
        my_url = self.survey_id.action_start_survey(answer=response)
        return my_url['url']

class RecruitmentEnhancement(models.Model):
    _name = 'hr.recruitment.interviews'

    assessment_date = fields.Date('Assessment Date')
    interviewer_id = fields.Many2one('res.users')
    performed_by_id = fields.Many2one('res.users')
    applicant_id = fields.Many2one('hr.applicant')
    survey_id = fields.Many2one('survey.survey')
    response_id = fields.Many2one('survey.user_input', "Response")
    score_percentage = fields.Float('Score Percentage')
    score_total = fields.Float('Total Score', compute='get_score')

    is_interviewer = fields.Boolean(compute='compute_is_interviewer')
    is_change_interviewer = fields.Boolean('Is Change Interviewer?', compute='compute_change_interviewer')

    def get_score(self):
        for rec in self:
            answer = rec.env['survey.user_input'].search([('id', '=', rec.response_id.id)])
            rec.score_total = answer.scoring_total
            rec.score_percentage = answer.scoring_percentage

    def compute_change_interviewer(self):
        record = self.env['res.groups'].search([('name', '=', 'Allow to Change Interviewer')])
        rec = self.env.user.id in record.users.ids
        if rec:
            data = True
        else:
            data = False
        self.is_change_interviewer = data

    def compute_is_interviewer(self):
        for rec in self:
            if rec.env.user.id == rec.interviewer_id.id:
                rec.is_interviewer = False
            else:
                rec.is_interviewer = True

    def action_start_survey(self):
        self.ensure_one()
        for rec in self:
            if rec.env.user.id == rec.interviewer_id.id:
                # create a response and link it to this applicant
                if not rec.response_id:
                    response = rec.survey_id._create_answer(partner=rec.performed_by_id)
                    rec.response_id = response.id
                else:
                    response = rec.response_id
                # grab the token of the response and start surveying
                # rec.score_percentage = response.scoring_percentage
                # rec.score_total = response.scoring_total
                rec.performed_by_id = rec._uid
                rec.assessment_date = datetime.today().date()
                return rec.survey_id.action_start_survey(answer=response)
            else:
                raise UserError('Sorry, this Interview is to be conducted by ' + rec.interviewer_id.name)

    def action_print_answers(self, answer=None):
        """ Open the website page with the survey form """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': "View Answers",
            'target': 'new',
            'url': '/survey/print/%s?answer_token=%s' % (self.survey_id.access_token, self.response_id.access_token)
        }

    # def action_print_answers(self):
    #     """ Open the website page with the survey form """
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'name': "View Answers",
    #         'target': 'self',
    #         'url': '/survey/print/%s?answer_token=%s' % (self.survey_id.access_token, self.access_token)
    #     }

    #
    # def action_print_survey(self):
    #     """ If response is available then print this response otherwise print survey form (print template of the survey) """
    #     self.ensure_one()
    #     for rec in self:
    #         print(rec.response_id)
    #         url = rec.survey_id.action_print_survey(answer=rec.response_id)
    #         return url

class SurveyUserInputInh(models.Model):
    _inherit = "survey.user_input"

    score = fields.Float('Score')

    @api.depends('user_input_line_ids.answer_score', 'user_input_line_ids.question_id',
                 'predefined_question_ids.answer_score')
    def _compute_scoring_values(self):
        for user_input in self:
            # sum(multi-choice question scores) + sum(simple answer_type scores)
            total_possible_score = 0
            for question in user_input.predefined_question_ids:
                if question.question_type == 'simple_choice':
                    total_possible_score += sum(
                        score for score in question.mapped('suggested_answer_ids.answer_score') if score > 0)
                elif question.question_type == 'multiple_choice':
                    score_list = []
                    for rec in question.suggested_answer_ids:
                        score_list.append(rec.answer_score)
                    total_possible_score += max(score_list)
                elif question.is_scored_question:
                    total_possible_score += question.answer_score

            if total_possible_score == 0:
                user_input.scoring_percentage = 0
                user_input.scoring_total = 0
            else:
                score_total = sum(user_input.user_input_line_ids.mapped('answer_score'))
                user_input.score = score_total
                user_input.scoring_total = score_total
                score_percentage = (score_total / total_possible_score) * 100
                user_input.scoring_percentage = round(score_percentage, 2) if score_percentage > 0 else 0


