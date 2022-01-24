from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrAppraisalFeedback(models.Model):
    _name = 'hr.appraisal.feedback'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    


    company_id = fields.Many2one('res.company', default=lambda self:self.env.company.id)
    description = fields.Char('Description')

    def action_send_mail_appraisee(self):
        mail_template = self.env.ref('de_appraisal_enhancement.mail_template_appraisal_objective_deadline')
        ctx = {
            'employee_to_name': self.name.name,
            'recipient_users': self.name.user_id,
            'url': '/mail/view?model=%s&res_id=%s' % ('hr.appraisal.objective', self.id),
        }
        RenderMixin = self.env['mail.render.mixin'].with_context(**ctx)
        subject = RenderMixin._render_template(mail_template.subject, 'hr.appraisal.feedback', self.ids, post_process=True)[self.id]
        body = RenderMixin._render_template(mail_template.body_html, 'hr.appraisal.feedback', self.ids, post_process=True)[self.id]
        mail_values = {
            'email_from': self.env.user.email_formatted,
            'author_id': self.env.user.partner_id.id,
            'model': None,
            'res_id': None,
            'subject': subject,
            'body_html': body,
            'auto_delete': True,
            'email_to': self.name.work_email
        }
        activity= self.env['mail.mail'].sudo().create(mail_values)
        activity.send()
    
    
    name = fields.Many2one('hr.employee',string = 'Name')
    job_title = fields.Char('Job Title', related = 'name.job_title')
    manager = fields.Char('Manager', related = 'name.parent_id.name')
    department = fields.Char('Department', related = 'name.department_id.name')
    date_joining = fields.Date('Date of Joining')
    grade = fields.Char('Grade')
    performance_period = fields.Selection([('2020', 'FY 2020-21'), 
                                           ('2021', 'FY 2021-22'), 
                                           ('2022', 'FY 2022-23'), 
                                           ('2023', 'FY 2023-24'),
                                           ('2024', 'FY 2024-25'), 
                                           ('2025', 'FY 2025-26'), 
                                           ('2026', 'FY 2026-27'), 
                                           ('2027', 'FY 2027-28'),
                                           ('2028', 'FY 2028-29'), 
                                           ('2029', 'FY 2029-30'), 
                                           ('2030', 'FY 2030-31'), 
                                           ('2031', 'FY 2031-32'),
                                           ('2032', 'FY 2032-33'),
                                           ('2033', 'FY 2033-34'), 
                                           ('2034', 'FY 2034-35'), 
                                           ('2035', 'FY 2035-36'), 
                                           ('2036', 'FY 2036-37'),
                                           ('2037', 'FY 2037-38'), 
                                           ('2038', 'FY 2038-39'), 
                                           ('2039', 'FY 2039-40'), 
                                           ('2040', 'FY 2040-41')],
                               string="Performance Period", readonly=True)
    
    note = fields.Text('Note', compute = 'get_default_note')   
    objective_comment = fields.Text('Emp. Half Year Comments')
    full_year_objective_comment = fields.Text('Manager Half Year Comments')
    value_comment = fields.Text('Emp. Half Year Comments')
    full_year_value_comment = fields.Text('Manager Half Year Comments')
    
    half_year_appraiser_objective_comment = fields.Text('Emp. Full year Comments')
    full_year_appraiser_objective_comment = fields.Text('Manager Full year Comments')
    half_year_appraiser_value_comment = fields.Text('Emp. Full year Comments')
    full_year_appraiser_value_comment = fields.Text('Manager Full year Comments')
    
    employee_feedback = fields.Char('Employee Feedback')
    future_aspiration = fields.Char('career aspirations in next 2 to 3 years')
    feedback_to_manager = fields.Char('Feedback to line manager')
    training_need = fields.Char('Training Need')
    rating_level = fields.Selection([
        ('Outstanding Performance', 'Outstanding Performance'),
        ('Excellent Performance', 'Excellent Performance'),
        ('Strong Performance', 'Strong Performance'),
        ('Needs Improvement', 'Needs Improvement'),
        ('Unsatisfactory', 'Unsatisfactory'),
    ], string='Rating Level', index=True, copy=False, compute='compute_total_rating_level')
    rating_score = fields.Float(string='Manager Rating Score', compute='compute_rating_level')
    rating_score_calc = fields.Float(string='Rating Score')
    employee_rating_level = fields.Selection([
        ('Outstanding Performance', 'Outstanding Performance'),
        ('Excellent Performance', 'Excellent Performance'),
        ('Strong Performance', 'Strong Performance'),
        ('Needs Improvement', 'Needs Improvement'),
        ('Unsatisfactory', 'Unsatisfactory'),
    ], string='Rating Level', index=True, copy=False, compute='compute_total_employee_rating_level')
    employee_rating_score = fields.Float(string='Manager Rating Score', compute='compute_employee_rating_level')
    employee_rating_score_calc = fields.Float(string='Employee Rating Score')


    def compute_employee_rating_level(self):
        for line in self:
            total_grand = 0
            half_year_obj_score = 0
            half_year_core_score = 0
            full_year_obj_score = 0
            full_year_core_score = 0
            for half_year_obj_line in line.feedback_objective_appraisee_lines:
                half_year_obj_score += half_year_obj_line.employee_rating_score
            for half_year_core_line in line.feedback_values_appraisee_lines:
                half_year_core_score += half_year_obj_line.employee_rating_score    
            for full_year_obj_line in line.feedback_objective_lines:
                full_year_obj_score += full_year_obj_line.employee_rating_score
            for full_year_core_line in line.feedback_values_lines:
                full_year_core_score += full_year_obj_line.employee_rating_score        
            total_grand = (((half_year_obj_score/5) * 90)/100) +  (((half_year_core_score/5) * 10)/100) + (((full_year_obj_score/5)*90)/100) + (((full_year_core_score/5)*10)/100) 
            line.update({
                'employee_rating_score': total_grand,
                'employee_rating_score_calc': total_grand,
            })  
    

    @api.depends('employee_rating_score')
    def compute_total_employee_rating_level(self):
        for line in self:
            if line.employee_rating_score >= 1 and line.employee_rating_score < 1.5:
                line.update({
                    'employee_rating_level': 'Unsatisfactory'
                })
            elif line.employee_rating_score >= 1.5 and line.employee_rating_score < 2.5:
                line.update({
                    'employee_rating_level': 'Needs Improvement'
                })   
            elif line.employee_rating_score >= 2.5 and line.employee_rating_score < 3.5:
                line.update({
                    'employee_rating_level': 'Strong Performance'
                })   
            elif line.employee_rating_score >= 3.5 and line.employee_rating_score < 4.5:
                line.update({
                    'employee_rating_level': 'Excellent Performance'
                })
            elif line.employee_rating_score >= 4.5 and line.employee_rating_score <= 5:
                line.update({
                    'employee_rating_level': 'Outstanding Performance'
                })
            elif line.employee_rating_score > 5:
                line.update({
                    'employee_rating_level': 'Outstanding Performance'
                })    
            else:
                line.update({
                    'employee_rating_level': False
                })           
    
    
    def compute_rating_level(self):
        for line in self:
            total_grand = 0
            half_year_obj_score = 0
            half_year_core_score = 0
            full_year_obj_score = 0
            full_year_core_score = 0
            for half_year_obj_line in line.feedback_objective_appraisee_lines:
                half_year_obj_score += half_year_obj_line.manager_rating_score
            for half_year_core_line in line.feedback_values_appraisee_lines:
                half_year_core_score += half_year_obj_line.manager_rating_score    
            for full_year_obj_line in line.feedback_objective_lines:
                full_year_obj_score += full_year_obj_line.manager_rating_score
            for full_year_core_line in line.feedback_values_lines:
                full_year_core_score += full_year_obj_line.manager_rating_score
            total_grand = (((half_year_obj_score/5) * 90)/100) +  (((half_year_core_score/5) * 10)/100) + (((full_year_obj_score/5)*90)/100) + (((full_year_core_score/5)*10)/100)          
            line.update({
                'rating_score': total_grand,
                'rating_score_calc': total_grand,
            })           
     
            
    @api.depends('rating_score')
    def compute_total_rating_level(self):
        for line in self:
            if line.rating_score >= 1 and line.rating_score < 1.5:
                line.update({
                    'rating_level': 'Unsatisfactory'
                })
            elif line.rating_score >= 1.5 and line.rating_score < 2.5:
                line.update({
                    'rating_level': 'Needs Improvement'
                })   
            elif line.rating_score >= 2.5 and line.rating_score < 3.5:
                line.update({
                    'rating_level': 'Strong Performance'
                })   
            elif line.rating_score >= 3.5 and line.rating_score < 4.5:
                line.update({
                    'rating_level': 'Excellent Performance'
                })
            elif line.rating_score >= 4.5 and line.rating_score <= 5:
                line.update({
                    'rating_level': 'Outstanding Performance'
                })
            elif line.rating_score > 5:
                line.update({
                    'rating_level': 'Outstanding Performance'
                })    
            else:
                line.update({
                    'rating_level': False
                })            
                
    
    def unlink(self):
    	for rec in self:
    		if rec.state not in ['draft']:
    			raise UserError(('Deletion is Not Allowed!'))
    		return super(HrAppraisalFeedback, self).unlink()
    
    
    @api.onchange('name')
    def get_default_note(self):
        self.note =  """                        5 = Outstanding      Ratings: 451-500
                        Consistently and significantly exceeds all performance expectations
                        and standards. Demonstrates a personal commitment to a high level
                        of performance and results, even under challenging work goals. 
                        
                        4 = Exceed Expectations  Ratings: 376- 450
                        Frequently exceeds job requirements. Makes contributions well
                        beyond job demands. Commendable performance.
                        
                        3 = Meet Expectations Ratings:  276 – 375
                        person in this position. All objectives and standards are meet. Has good
                        job knowledge and is able to perform with minimum supervision.
                        
                        2 = Partially Meet Expectations Ratings: 200 – 275
                        totally achieved. Person is capable of improving to an acceptable
                        standard.
                        
                        1 = Unacceptable performance  Ratings: Below 200
                        An individual who has performed inadequately in the objectives set for
                        her/his position.
       """
        
    mid_year_date = fields.Date('Mid Year Review Date')
    end_year_date = fields.Date('End Year Review Date')
    date_end_deadline = fields.Date('End Year Deadline Date')
    date_mid_deadline = fields.Date('Mid Year Deadline Date')
    
    objective_score = fields.Float('Business Objectives Accumulative Score', compute='compute_objective_score')
    objective_rating = fields.Char('Business Objectives Accumulative Rating')
    
    behavioral_score = fields.Float('Behavioral Accumulative Score', compute='compute_core_score')
    behavioral_rating = fields.Char('Behavioral Accumulative Rating')
    
    agreement = fields.Selection([
        ('not_agree', 'Not Agree'),
        ('partially', 'Partially Agree'),
        ('fully', 'Fully Agree'),
    ], string='Agreement With Half Year Evaluation', index=True, copy=False, default='partially', required = True, track_visibility='onchange')
    
    full_year_agreement = fields.Selection([
        ('not_agree', 'Not Agree'),
        ('partially', 'Partially Agree'),
        ('fully', 'Fully Agree'),
    ], string='Agreement With Full Year Evaluation', index=True, copy=False, default='partially', required = True, track_visibility='onchange')
    
    reason_for_disagreement = fields.Char('Reason For Disagreement')
    full_reason_for_disagreement = fields.Char('Full Year Reason For Disagreement')
    
    concerned_person = fields.Selection([
        ('employee', 'Employee'),
        ('manager', 'Manager'),
    ], string='Concerned Person', index=True, copy=False, default='employee', required = True, track_visibility='onchange')
    
    
    appraisal_period = fields.Selection([
        ('half_year', 'Half Year'),
        ('full_year', 'Full Year'),

    ], string='Appraisal Period', index=True, copy=False, default='half_year', required = True, track_visibility='onchange')
            
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('expired', 'Expired'),
        ('sent', 'Sent for Employee Review'),
        ('endorsed_employee', 'Endorsed by Employee'),
        ('endorsed_hod', 'Endorsed by HOD'),
        ('done', 'Done'),
        ('end_year_appraisee_review', 'End Year Appraisee Review'),
        ('end_year_appraiser_review', 'End Year Appraiser Review'),
        ('end_year_sent_emp_view', 'End Year Sent for Emp Review'),
        ('end_year_endorsed_emp', 'End Year Endorsed by Emp'),
        ('end_year_endorse_hod', 'End Year Endorsed by HOD'),
        ('closed', 'Closed'),
        
    ], string='State', index=True, copy=False, default='draft', track_visibility='onchange', tracking=True)
    
    def action_refuse(self):
        for line in self:
            if line.state=='endorsed_employee':
                line.update({
                    'state': 'sent'
                })
            elif line.state=='end_year_endorsed_emp':
                line.update({
                    'state': 'end_year_sent_emp_view'
                })    
    
    feedback_objective_lines = fields.One2many('hr.appraisal.feedback.objective.line', 'feedback_id', tracking=True, track_visibility='onchange')
    feedback_values_lines = fields.One2many('hr.appraisal.feedback.values.line', 'feedback_id', tracking=True, track_visibility='onchange')
    feedback_promotion_lines = fields.One2many('hr.appraisal.feedback.promotion.line', 'feedback_id')
    feedback_training_lines = fields.One2many('hr.appraisal.feedback.training.line', 'feedback_id')
    feedback_objective_appraisee_lines = fields.One2many('hr.appraisal.feedback.objective.appraisee.line', 'feedback_id')
    feedback_values_appraisee_lines = fields.One2many('hr.appraisal.feedback.values.appraisee.line', 'feedback_id')
    
    
    strength_1 = fields.Char('Strengths/Achievements')
    strength_2 = fields.Char('strength')
    strength_3= fields.Char('strength')
    strength_4 = fields.Char('strength')
    strength_5= fields.Char('strength')

    improvements_1 = fields.Char('Weaknesses/Areas for Improvement')
    improvements_2 = fields.Char('improvements')
    improvements_3 = fields.Char('improvements')
    improvements_4 = fields.Char('improvements')
    improvements_5 = fields.Char('improvements')
    
    reason_1 = fields.Char('reason')
    reason_2 = fields.Char('reason')
    reason_3 = fields.Char('reason')
    reason_4 = fields.Char('reason')
    reason_5 = fields.Char('reason')
    
    training_1 = fields.Char('Training')
    training_2 = fields.Char('Training')
    training_3 = fields.Char('Training')
    training_4 = fields.Char('Training')
    training_5= fields.Char('Training')

    
    recommend_promotion = fields.Selection([('yes', 'Yes'),('no', 'No'),
    ], string='Recommended for Promotion?', index=True, copy=False, default='no',  required=True, track_visibility='onchange')
    promotion_position = fields.Char('Promotion To Position')
    promotion_grade = fields.Char('Promotion To Grade')
    date_effective = fields.Date('With Effect From')
    
    
    @api.onchange('recommend_promotion')
    def promotion_check(self):
        if self.recommend_promotion:
            for rec in self:
                rec.update({
                    'promotion_position' : '',
                    'promotion_grade' : '',
                    'date_effective' : '',
                })
    
    @api.onchange('agreement')
    def agreement_check(self):
        if self.agreement:
            for rec in self:
                rec.update({
                    'reason_for_disagreement':''
                })
                
    @api.onchange('full_year_agreement')
    def agreement_full_check(self):
        if self.agreement:
            for rec in self:
                rec.update({
                    'full_reason_for_disagreement':''
                })
    
    
    @api.onchange('feedback_objective_lines')
    def track_history(self):
        self.message_notify(body=_('Changes Recording'))
    
    @api.onchange('feedback_values_lines')
    def track_history(self):
        self.message_notify(body=_('Dear %s, Changes Recorded') % (self.env.user.name,), partner_ids=[self.env.user.partner_id.id])

    
    def compute_objective_score(self):
        sum = 0
        if self.feedback_objective_lines:
            for rec in self.feedback_objective_lines:
                sum = sum + rec.weightage_score_mngr
        self.objective_score = sum
        if round(self.objective_score,0) in range(451,501):
            self.objective_rating = 'Outstanding'
            
        elif round(self.objective_score,0) in range(376,451):
            self.objective_rating = 'Exceed Expectations'
        
        elif round(self.objective_score,0) in range(276,376):
            self.objective_rating = 'Meet Expectations'
        elif round(self.objective_score,0) in range(200,276):
            self.objective_rating = 'Partially Meet Expectations'
        elif round(self.objective_score,0) in range(1,200):
            self.objective_rating = 'Unacceptable'
        else:
            self.objective_rating = ' '
            
    
    def compute_core_score(self):
        sum = 0
        if self.feedback_values_lines:
            for rec in self.feedback_values_lines:
                sum = sum + rec.weightage_score_mngr
        self.behavioral_score = sum
        
        if round(self.behavioral_score,0) in range(451,501):
            self.behavioral_rating = 'Outstanding'
        elif round(self.behavioral_score,0) in range(376,451):
            self.behavioral_rating = 'Exceed Expectations'
        elif round(self.behavioral_score,0) in range(276,376):
            self.behavioral_rating = 'Meet Expectations'
        elif round(self.behavioral_score,0) in range(200,276):
            self.behavioral_rating = 'Partially Meet Expectations'
        elif round(self.behavioral_score,0) in range(1,200):
            self.behavioral_rating = 'Unacceptable'
        else:
            self.behavioral_rating = ' '
            
    def action_send_mail_appraisal(self):
        mail_template = self.env.ref('de_appraisal_enhancement.mail_template_appraisal_feedback_m_create')
        ctx = {
            'employee_to_name': self.name.name,
            'recipient_users': self.name.user_id,
            'url': '/appraisal/feedback/%s' % (self.id),
        }
        RenderMixin = self.env['mail.render.mixin'].with_context(**ctx)
        subject = RenderMixin._render_template(mail_template.subject, 'hr.appraisal.feedback', self.ids, post_process=True)[self.id]
        body = RenderMixin._render_template(mail_template.body_html, 'hr.appraisal.feedback', self.ids, post_process=True)[self.id]
        mail_values = {
            'email_from': self.env.user.email_formatted,
            'author_id': self.env.user.partner_id.id,
            'model': None,
            'res_id': None,
            'subject': subject,
            'body_html': body,
            'auto_delete': True,
            'email_to': self.name.work_email
        }
        activity= self.env['mail.mail'].sudo().create(mail_values)
        activity.send()


    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        rslt = super(HrAppraisalFeedback, self).create(vals_list)
        rslt.action_send_mail_appraisal()
        return rslt
            
    
    def action_send_manager_mail(self):
        mail_template = self.env.ref('de_appraisal_enhancement.mail_template_appraisal_feedback_m1')
        ctx = {
            'employee_to_name': self.name.parent_id.name,
            'recipient_users': self.name.parent_id.user_id,
            'url': '/appraisal/feedback/%s' % (self.id),
        }
        RenderMixin = self.env['mail.render.mixin'].with_context(**ctx)
        subject = RenderMixin._render_template(mail_template.subject, 'hr.appraisal.feedback', self.ids, post_process=True)[self.id]
        body = RenderMixin._render_template(mail_template.body_html, 'hr.appraisal.feedback', self.ids, post_process=True)[self.id]
        mail_values = {
            'email_from': self.env.user.email_formatted,
            'author_id': self.env.user.partner_id.id,
            'model': None,
            'res_id': None,
            'subject': subject,
            'body_html': body,
            'auto_delete': True,
            'email_to': self.name.parent_id.work_email
        }
        activity= self.env['mail.mail'].sudo().create(mail_values)
        activity.send()


    def action_send_manager_mail_reply(self):
        mail_template = self.env.ref('de_appraisal_enhancement.mail_template_appraisal_feedback_m2')
        ctx = {
            'employee_to_name': self.name.name,
            'recipient_users': self.name.user_id,
            'url': '/appraisal/feedback/%s' % (self.id),
        }
        RenderMixin = self.env['mail.render.mixin'].with_context(**ctx)
        subject = RenderMixin._render_template(mail_template.subject, 'hr.appraisal.feedback', self.ids, post_process=True)[self.id]
        body = RenderMixin._render_template(mail_template.body_html, 'hr.appraisal.feedback', self.ids, post_process=True)[self.id]
        mail_values = {
            'email_from': self.env.user.email_formatted,
            'author_id': self.env.user.partner_id.id,
            'model': None,
            'res_id': None,
            'subject': subject,
            'body_html': body,
            'auto_delete': True,
            'email_to': self.name.work_email
        }
        activity= self.env['mail.mail'].sudo().create(mail_values)
        activity.send()


    def action_send_hod_mail(self):
        mail_template = self.env.ref('de_appraisal_enhancement.mail_template_appraisal_feedback_m3')
        ctx = {
            'employee_to_name': self.name.department_id.manager_id.name,
            'recipient_users': self.name.department_id.manager_id.user_id,
            'url': '/appraisal/feedback/%s' % (self.id),
        }
        RenderMixin = self.env['mail.render.mixin'].with_context(**ctx)
        subject = RenderMixin._render_template(mail_template.subject, 'hr.appraisal.feedback', self.ids, post_process=True)[self.id]
        body = RenderMixin._render_template(mail_template.body_html, 'hr.appraisal.feedback', self.ids, post_process=True)[self.id]
        mail_values = {
            'email_from': self.env.user.email_formatted,
            'author_id': self.env.user.partner_id.id,
            'model': None,
            'res_id': None,
            'subject': subject,
            'body_html': body,
            'auto_delete': True,
            'email_to': self.name.department_id.manager_id.work_email
        }
        activity= self.env['mail.mail'].sudo().create(mail_values)
        activity.send()



    def action_send_mail_appraisal_done(self):
        mail_template = self.env.ref('de_appraisal_enhancement.mail_template_appraisal_feedback_m4')
        ctx = {
            'employee_to_name': self.name.name,
            'recipient_users': self.name.user_id,
            'url': '/appraisal/feedback/%s' % (self.id),
        }
        RenderMixin = self.env['mail.render.mixin'].with_context(**ctx)
        subject = RenderMixin._render_template(mail_template.subject, 'hr.appraisal.feedback', self.ids, post_process=True)[self.id]
        body = RenderMixin._render_template(mail_template.body_html, 'hr.appraisal.feedback', self.ids, post_process=True)[self.id]
        mail_values = {
            'email_from': self.env.user.email_formatted,
            'author_id': self.env.user.partner_id.id,
            'model': None,
            'res_id': None,
            'subject': subject,
            'body_html': body,
            'auto_delete': True,
            'email_to': self.name.work_email
        }
        activity= self.env['mail.mail'].sudo().create(mail_values)
        activity.send()



    
    def action_confirm(self):
        self.state = 'confirm'
        self.action_send_manager_mail()
    

    def employee_done(self):
        self.state = 'done'
    
#     def action_expired(self):
#         self.state = 'expired'
        
    def action_Sent_for_Employee_Review(self):
        self.state = 'sent'
        self.action_send_manager_mail_reply()

        
    def action_endorsed_employee(self):
        self.state = 'endorsed_employee'
        self.action_send_hod_mail()
        
    def action_endorsed_hod(self):
        self.state = 'endorsed_hod'
        
    def action_done(self):
        self.state = 'done'
        self.action_send_mail_appraisal_done()
#         States After Done Controlled Here

    def action_end_year_appraisee_review(self):
        self.state = 'end_year_appraisee_review'
        self.action_send_mail_appraisal()
        
    def action_end_year_appraiser_review(self):
        self.state = 'end_year_appraiser_review'
        self.action_send_manager_mail()
        
    def action_end_year_sent_emp_view(self):
        self.state = 'end_year_sent_emp_view'
        self.action_send_manager_mail_reply()
        
    def action_end_year_endorsed_emp(self):
        self.state = 'end_year_endorsed_emp'
        self.action_send_hod_mail()

        
    def action_end_year_endorse_hod(self):
        self.state = 'end_year_endorse_hod'
        
    def action_closed(self):
        self.state = 'closed'
        self.action_send_mail_appraisal_done()

        
    

class HrAppraisalFeedbackObjectiveLine(models.Model):
    _name = 'hr.appraisal.feedback.objective.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    feedback_id = fields.Many2one('hr.appraisal.feedback')
    appraisal_period = fields.Selection(related='feedback_id.appraisal_period')
    concerned_person = fields.Selection(related='feedback_id.concerned_person')
    full_remarks = fields.Char('Emp. Remarks')
    objective = fields.Char('Objective')
    obj_description = fields.Char('Description')
    weightage = fields.Float('Weightage')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ], string='Priority', index=True, copy=False, default='low', required = True, track_visibility='onchange')
    rating = fields.Integer('Emp. Full Year Rating', track_visibility='onchange')
    comments = fields.Char('Comments')   
    full_remarks_mngr = fields.Char('Manager Remarks')
    rating_mngr = fields.Integer('Manager Full Year Rating')
    weightage_score_mngr = fields.Float('Weightage Score', compute='compute_weightage_score')   
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('expired', 'Expired'),
        ('sent', 'Sent for Employee Review'),
        ('endorsed_employee', 'Endorsed by Employee'),
        ('endorsed_hod', 'Endorsed by HOD'),
        ('done', 'Done'),
        ('end_year_appraisee_review', 'End Year Appraisee Review'),
        ('end_year_appraiser_review', 'End Year Appraiser Review'),
        ('end_year_sent_emp_view', 'End Year Sent for Emp Review'),
        ('end_year_endorsed_emp', 'End Year Endorsed by Emp'),
        ('end_year_endorse_hod', 'End Year Endorsed by HOD'),
        ('closed', 'Closed'),
        
    ], string='State', related='feedback_id.state')
    manager_rating_level = fields.Selection([
        ('Outstanding Performance', 'Outstanding Performance'),
        ('Excellent Performance', 'Excellent Performance'),
        ('Strong Performance', 'Strong Performance'),
        ('Needs Improvement', 'Needs Improvement'),
        ('Unsatisfactory', 'Unsatisfactory'),
    ], string='Manager Rating Level', index=True, copy=False)
    employee_rating_level = fields.Selection([
        ('Outstanding Performance', 'Outstanding Performance'),
        ('Excellent Performance', 'Excellent Performance'),
        ('Strong Performance', 'Strong Performance'),
        ('Needs Improvement', 'Needs Improvement'),
        ('Unsatisfactory', 'Unsatisfactory'),
    ], string='Employee Rating Level', index=True, copy=False)
    manager_rating_score = fields.Float(string='Mnanager Rating Score', compute='compute_manager_rating_level')
    employee_rating_score = fields.Float(string='Employee Rating Score', compute='compute_employee_rating_score')
    
    @api.depends('manager_rating_level')
    def compute_manager_rating_level(self):
        for line in self:
            if line.manager_rating_level == 'Unsatisfactory':
                line.update({
                    'manager_rating_score': 1
                })
            elif line.manager_rating_level == 'Needs Improvement':
                line.update({
                    'manager_rating_score': 2
                })   
            elif line.manager_rating_level == 'Strong Performance':
                line.update({
                    'manager_rating_score': 3
                })   
            elif line.manager_rating_level == 'Excellent Performance':
                line.update({
                    'manager_rating_score': 4
                })
            elif line.manager_rating_level == 'Outstanding Performance':
                line.update({
                    'manager_rating_score': 5
                }) 
            else:
                line.update({
                    'manager_rating_score': 0
                })   
                
                
    @api.depends('employee_rating_level')
    def compute_employee_rating_score(self):
        for line in self:
            if line.employee_rating_level == 'Unsatisfactory':
                line.update({
                    'employee_rating_score': 1
                })
            elif line.employee_rating_level == 'Needs Improvement':
                line.update({
                    'employee_rating_score': 2
                })   
            elif line.employee_rating_level == 'Strong Performance':
                line.update({
                    'employee_rating_score': 3
                })   
            elif line.employee_rating_level == 'Excellent Performance':
                line.update({
                    'employee_rating_score': 4
                })
            elif line.employee_rating_level == 'Outstanding Performance':
                line.update({
                    'employee_rating_score': 5
                }) 
            else:
                line.update({
                    'employee_rating_score': 0
                })               
                
      
    
    def compute_weightage_score(self):
        for rec in self:
            rec.weightage_score_mngr = rec.weightage * (rec.rating_mngr / 100)
    
    @api.onchange('rating')
    def limit_rating(self):
        if self.rating:
            for rec in self:
                if rec.rating > 500 or rec.rating <= 0:
                    raise UserError('Rating Cannot be greater than 500 or less than 1')
    


class HrAppraisalFeedbackValuesLine(models.Model):
    _name = 'hr.appraisal.feedback.values.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    feedback_id = fields.Many2one('hr.appraisal.feedback')
    appraisal_period = fields.Selection(related='feedback_id.appraisal_period')
    concerned_person = fields.Selection(related='feedback_id.concerned_person')
    full_remarks = fields.Char('Emp. Remarks')
    core_values = fields.Char('Core Values')
    core_description = fields.Char('Description')
    weightage = fields.Float('Weightage')
    
    full_remarks_mngr = fields.Char('Manager Remarks')
    rating_mngr = fields.Integer('Manager Full Year Rating')
    weightage_score_mngr = fields.Float('Weightage Score', compute='compute_weightage_score')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ], string='Priority', index=True, copy=False, default='low', required = True,track_visibility='onchange')
    rating = fields.Integer('Emp. Full Year Rating', track_visibility=True)
#     weightage_score = fields.Float('Weightage Score', compute='compute_weightage_score')
    comments = fields.Char('Comments')
    
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('expired', 'Expired'),
        ('sent', 'Sent for Employee Review'),
        ('endorsed_employee', 'Endorsed by Employee'),
        ('endorsed_hod', 'Endorsed by HOD'),
        ('done', 'Done'),
        ('end_year_appraisee_review', 'End Year Appraisee Review'),
        ('end_year_appraiser_review', 'End Year Appraiser Review'),
        ('end_year_sent_emp_view', 'End Year Sent for Emp Review'),
        ('end_year_endorsed_emp', 'End Year Endorsed by Emp'),
        ('end_year_endorse_hod', 'End Year Endorsed by HOD'),
        ('closed', 'Closed'),
        
    ], string='State', related='feedback_id.state')
    manager_rating_level = fields.Selection([
        ('Outstanding Performance', 'Outstanding Performance'),
        ('Excellent Performance', 'Excellent Performance'),
        ('Strong Performance', 'Strong Performance'),
        ('Needs Improvement', 'Needs Improvement'),
        ('Unsatisfactory', 'Unsatisfactory'),
    ], string='Manager Rating Level', index=True, copy=False)
    employee_rating_level = fields.Selection([
        ('Outstanding Performance', 'Outstanding Performance'),
        ('Excellent Performance', 'Excellent Performance'),
        ('Strong Performance', 'Strong Performance'),
        ('Needs Improvement', 'Needs Improvement'),
        ('Unsatisfactory', 'Unsatisfactory'),
    ], string='Employee Rating Level', index=True, copy=False)
    manager_rating_score = fields.Float(string='Mnanager Rating Score', compute='compute_manager_rating_level')
    employee_rating_score = fields.Float(string='Employee Rating Score', compute='compute_employee_rating_score')
    
    @api.depends('manager_rating_level')
    def compute_manager_rating_level(self):
        for line in self:
            if line.manager_rating_level == 'Unsatisfactory':
                line.update({
                    'manager_rating_score': 1
                })
            elif line.manager_rating_level == 'Needs Improvement':
                line.update({
                    'manager_rating_score': 2
                })   
            elif line.manager_rating_level == 'Strong Performance':
                line.update({
                    'manager_rating_score': 3
                })   
            elif line.manager_rating_level == 'Excellent Performance':
                line.update({
                    'manager_rating_score': 4
                })
            elif line.manager_rating_level == 'Outstanding Performance':
                line.update({
                    'manager_rating_score': 5
                }) 
            else:
                line.update({
                    'manager_rating_score': 0
                })   
                
                
    @api.depends('employee_rating_level')
    def compute_employee_rating_score(self):
        for line in self:
            if line.employee_rating_level == 'Unsatisfactory':
                line.update({
                    'employee_rating_score': 1
                })
            elif line.employee_rating_level == 'Needs Improvement':
                line.update({
                    'employee_rating_score': 2
                })   
            elif line.employee_rating_level == 'Strong Performance':
                line.update({
                    'employee_rating_score': 3
                })   
            elif line.employee_rating_level == 'Excellent Performance':
                line.update({
                    'employee_rating_score': 4
                })
            elif line.employee_rating_level == 'Outstanding Performance':
                line.update({
                    'employee_rating_score': 5
                }) 
            else:
                line.update({
                    'employee_rating_score': 0
                })               
                
 
      
    
    
    def compute_weightage_score(self):
        for rec in self:
            rec.weightage_score_mngr = rec.weightage * (rec.rating_mngr / 100)
    
    @api.onchange('rating')
    def limit_rating(self):
        if self.rating:
            for rec in self:
                if rec.rating > 500 or rec.rating <= 0:
                    raise UserError('Rating Cannot be greater than 500 or less than 1')
    
class HrAppraisalFeedbackPromotionLine(models.Model):
    _name = 'hr.appraisal.feedback.promotion.line'
    
    feedback_id = fields.Many2one('hr.appraisal.feedback')
    appraisal_period = fields.Selection(related='feedback_id.appraisal_period')
    concerned_person = fields.Selection(related='feedback_id.concerned_person')
    
    recommend_promotion = fields.Selection([('yes', 'Yes'),('no', 'No'),
    ], string='Recommended for Promotion?', index=True, copy=False, default='no',  required=True, track_visibility='onchange')
    promotion_position = fields.Char('Promotion To Position')
    promotion_grade = fields.Char('Promotion To Grade')
    date_effective = fields.Date('With Effect From')
    
    
class HrAppraisalFeedbackTrainingLine(models.Model):
    _name = 'hr.appraisal.feedback.training.line'
    
    feedback_id = fields.Many2one('hr.appraisal.feedback')
    appraisal_period = fields.Selection(related='feedback_id.appraisal_period')
    concerned_person = fields.Selection(related='feedback_id.concerned_person')
    
    strength = fields.Char('Strengths/Achievements')
    improvements = fields.Char('Weaknesses/Areas for Improvement')
    training = fields.Char('Training Recommend')
    reason = fields.Char('Reason')

    
    
    
    
class HrAppraisalFeedbackObjectiveAppraiseeLine(models.Model):
    _name = 'hr.appraisal.feedback.objective.appraisee.line'

    feedback_id = fields.Many2one('hr.appraisal.feedback')
    appraisal_period = fields.Selection(related='feedback_id.appraisal_period')
    concerned_person = fields.Selection(related='feedback_id.concerned_person')
    remarks = fields.Char('Emp. Remarks')
    remarks_mngr = fields.Char('Manager Remarks')
    objective = fields.Char('Objective')
    obj_description = fields.Char('Description')
    weightage = fields.Float('Weightage')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ], string='Priority',default='low')
    percentage_score = fields.Selection([
        ('0', '0%'),
        ('1', '10%'),
        ('2', '20%'),
        ('3', '30%'),
        ('4', '40%'),
        ('5', '50%'),
        ('6', '60%'),
        ('7', '70%'),
        ('8', '80%'),
        ('9', '90%'),
        ('10', '100%'),
    ], string='Emp. Half Year % Score', default='0')
    percentage_score_mngr = fields.Selection([
        ('0', '0%'),
        ('1', '10%'),
        ('2', '20%'),
        ('3', '30%'),
        ('4', '40%'),
        ('5', '50%'),
        ('6', '60%'),
        ('7', '70%'),
        ('8', '80%'),
        ('9', '90%'),
        ('10', '100%'),
    ], string='Manager Half Year % Score', index=True, copy=False, default='0',required = True, track_visibility='onchange')
    comments = fields.Char('Comments')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('expired', 'Expired'),
        ('sent', 'Sent for Employee Review'),
        ('endorsed_employee', 'Endorsed by Employee'),
        ('endorsed_hod', 'Endorsed by HOD'),
        ('done', 'Done'),
        ('end_year_appraisee_review', 'End Year Appraisee Review'),
        ('end_year_appraiser_review', 'End Year Appraiser Review'),
        ('end_year_sent_emp_view', 'End Year Sent for Emp Review'),
        ('end_year_endorsed_emp', 'End Year Endorsed by Emp'),
        ('end_year_endorse_hod', 'End Year Endorsed by HOD'),
        ('closed', 'Closed'),
        
    ], string='State', related='feedback_id.state')
    manager_rating_level = fields.Selection([
        ('Outstanding Performance', 'Outstanding Performance'),
        ('Excellent Performance', 'Excellent Performance'),
        ('Strong Performance', 'Strong Performance'),
        ('Needs Improvement', 'Needs Improvement'),
        ('Unsatisfactory', 'Unsatisfactory'),
    ], string='Manager Rating Level', index=True, copy=False)
    employee_rating_level = fields.Selection([
        ('Outstanding Performance', 'Outstanding Performance'),
        ('Excellent Performance', 'Excellent Performance'),
        ('Strong Performance', 'Strong Performance'),
        ('Needs Improvement', 'Needs Improvement'),
        ('Unsatisfactory', 'Unsatisfactory'),
    ], string='Employee Rating Level', index=True, copy=False, )
    manager_rating_score = fields.Float(string='Mnanager Rating Score', compute='compute_manager_rating_level')
    employee_rating_score = fields.Float(string='Employee Rating Score',compute='compute_employee_rating_score')
    
    @api.depends('manager_rating_level')
    def compute_manager_rating_level(self):
        for line in self:
            if line.manager_rating_level == 'Unsatisfactory':
                line.update({
                    'manager_rating_score': 1
                })
            elif line.manager_rating_level == 'Needs Improvement':
                line.update({
                    'manager_rating_score': 2
                })   
            elif line.manager_rating_level == 'Strong Performance':
                line.update({
                    'manager_rating_score': 3
                })   
            elif line.manager_rating_level == 'Excellent Performance':
                line.update({
                    'manager_rating_score': 4
                })
            elif line.manager_rating_level == 'Outstanding Performance':
                line.update({
                    'manager_rating_score': 5
                }) 
            else:
                line.update({
                    'manager_rating_score': 0
                })   
                
                
    @api.depends('employee_rating_level')
    def compute_employee_rating_score(self):
        for line in self:
            if line.employee_rating_level == 'Unsatisfactory':
                line.update({
                    'employee_rating_score': 1
                })
            elif line.employee_rating_level == 'Needs Improvement':
                line.update({
                    'employee_rating_score': 2
                })   
            elif line.employee_rating_level == 'Strong Performance':
                line.update({
                    'employee_rating_score': 3
                })   
            elif line.employee_rating_level == 'Excellent Performance':
                line.update({
                    'employee_rating_score': 4
                })
            elif line.employee_rating_level == 'Outstanding Performance':
                line.update({
                    'employee_rating_score': 5
                }) 
            else:
                line.update({
                    'employee_rating_score': 0
                })               
                
 
    def compute_weightage_score(self):
        for rec in self:
            rec.weightage_score_mngr = rec.weightage * (rec.rating_mngr / 100)
    
    @api.onchange('rating')
    def limit_rating(self):
        if self.rating:
            for rec in self:
                if rec.rating > 500 or rec.rating <= 0:
                    raise UserError('Rating Cannot be greater than 500 or less than 1')
    
    
class HrAppraisalFeedbackValuesAppraiseeLine(models.Model):
    _name = 'hr.appraisal.feedback.values.appraisee.line'
    
    feedback_id = fields.Many2one('hr.appraisal.feedback')
    appraisal_period = fields.Selection(related='feedback_id.appraisal_period')
    concerned_person = fields.Selection(related='feedback_id.concerned_person')
    remarks = fields.Char('Emp. Remarks')
    remarks_mngr = fields.Char('Manager Remarks')
    core_values = fields.Char('Core Values')
    core_description = fields.Char('Description')
    weightage = fields.Float('Weightage')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ], string='Priority', default='low')
    comments = fields.Char('Comments')
    conformance_level = fields.Selection([
        ('below', 'Below Average'),
        ('satisfactory', 'Satisfactory'),
        ('good', 'Good'),
        ('role_model', 'Role Model'),
    ], string='Emp: Half Year Conformance', default='satisfactory')
    conformance_level_mngr = fields.Selection([
        ('below', 'Below Average'),
        ('satisfactory', 'Satisfactory'),
        ('good', 'Good'),
        ('role_model', 'Role Model'),
    ], string='Manager: Half Year Conformance', default='satisfactory')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('expired', 'Expired'),
        ('sent', 'Sent for Employee Review'),
        ('endorsed_employee', 'Endorsed by Employee'),
        ('endorsed_hod', 'Endorsed by HOD'),
        ('done', 'Done'),
        ('end_year_appraisee_review', 'End Year Appraisee Review'),
        ('end_year_appraiser_review', 'End Year Appraiser Review'),
        ('end_year_sent_emp_view', 'End Year Sent for Emp Review'),
        ('end_year_endorsed_emp', 'End Year Endorsed by Emp'),
        ('end_year_endorse_hod', 'End Year Endorsed by HOD'),
        ('closed', 'Closed'),
        
    ], string='State', related='feedback_id.state')
    manager_rating_level = fields.Selection([
        ('Outstanding Performance', 'Outstanding Performance'),
        ('Excellent Performance', 'Excellent Performance'),
        ('Strong Performance', 'Strong Performance'),
        ('Needs Improvement', 'Needs Improvement'),
        ('Unsatisfactory', 'Unsatisfactory'),
    ], string='Manager Rating Level', index=True, copy=False)
    employee_rating_level = fields.Selection([
        ('Outstanding Performance', 'Outstanding Performance'),
        ('Excellent Performance', 'Excellent Performance'),
        ('Strong Performance', 'Strong Performance'),
        ('Needs Improvement', 'Needs Improvement'),
        ('Unsatisfactory', 'Unsatisfactory'),
    ], string='Employee Rating Level', index=True, copy=False)
    manager_rating_score = fields.Float(string='Mnanager Rating Score', compute='compute_manager_rating_level')
    employee_rating_score = fields.Float(string='Employee Rating Score', compute='compute_employee_rating_score')
    
    @api.depends('manager_rating_level')
    def compute_manager_rating_level(self):
        for line in self:
            if line.manager_rating_level == 'Unsatisfactory':
                line.update({
                    'manager_rating_score': 1
                })
            elif line.manager_rating_level == 'Needs Improvement':
                line.update({
                    'manager_rating_score': 2
                })   
            elif line.manager_rating_level == 'Strong Performance':
                line.update({
                    'manager_rating_score': 3
                })   
            elif line.manager_rating_level == 'Excellent Performance':
                line.update({
                    'manager_rating_score': 4
                })
            elif line.manager_rating_level == 'Outstanding Performance':
                line.update({
                    'manager_rating_score': 5
                }) 
            else:
                line.update({
                    'manager_rating_score': 0
                })   
                
                
    @api.depends('employee_rating_level')
    def compute_employee_rating_score(self):
        for line in self:
            if line.employee_rating_level == 'Unsatisfactory':
                line.update({
                    'employee_rating_score': 1
                })
            elif line.employee_rating_level == 'Needs Improvement':
                line.update({
                    'employee_rating_score': 2
                })   
            elif line.employee_rating_level == 'Strong Performance':
                line.update({
                    'employee_rating_score': 3
                })   
            elif line.employee_rating_level == 'Excellent Performance':
                line.update({
                    'employee_rating_score': 4
                })
            elif line.employee_rating_level == 'Outstanding Performance':
                line.update({
                    'employee_rating_score': 5
                }) 
            else:
                line.update({
                    'employee_rating_score': 0
                })               
                         
    
    
    def compute_weightage_score(self):
        for rec in self:
            rec.weightage_score_mngr = rec.weightage * (rec.rating_mngr / 100)
    
    @api.onchange('rating')
    def limit_rating(self):
        if self.rating:
            for rec in self:
                if rec.rating > 500 or rec.rating <= 0:
                    raise UserError('Rating Cannot be greater than 500 or less than 1')