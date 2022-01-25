from odoo import api, fields, models, _
from odoo.exceptions import UserError

class HrAppraisalObjective(models.Model):
    _name = 'hr.appraisal.objective'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description='Appraisal Objective'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee',string='Employee')
    emploee_code = fields.Char(related='employee_id.emp_number')
    emploee_type = fields.Selection(related='employee_id.emp_type')
    company_id = fields.Many2one('res.company', string='Company', compute='_compute_employee_company', store=True)
    grade_type_id = fields.Many2one(related='employee_id.grade_type')
    is_posted = fields.Boolean(string='Appraisal Created')
    department_id = fields.Many2one('hr.department', string='Department')
    job_id = fields.Many2one(related='employee_id.job_id')
    description = fields.Char('Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', "Sent for Manager's review"),
        ('confirm', 'Confirmed'),
    ], string='State', index=True, copy=False, default='draft', track_visibility='onchange')    
    objective_year = fields.Selection([('2020', 'FY 2020-21'), 
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
                               string="Objective Year", default='2021', required=True)
   
    objective_lines = fields.One2many('hr.appraisal.objective.line', 'objective_id')
    traing_need = fields.Char(string='Training Need')
    total_weightage = fields.Float("Total Weightage", compute = 'limit_weightage')
    note = fields.Text(string='Achivements')
    readonly_status = fields.Selection([
        ('make_readonly', 'Readonly'),
        ('make_editable', 'Editable')], compute = 'compute_readonly')
    work_location_id = fields.Many2one('hr.work.location',string='Work Location')
    cwork_location_id = fields.Many2one('hr.work.location',string='cWork Location', compute='_compute_work_locationn')
    
    
    
    
    def action_send_mail(self):
        mail_template = self.env.ref('de_appraisal_enhancement.mail_template_appraisal_objective')
        ctx = {
            'employee_to_name': self.employee_id.parent_id.name,
            'recipient_users': self.employee_id.user_id,
            'url': '/mail/view?model=%s&res_id=%s' % ('hr.appraisal.objective', self.id),
        }
        RenderMixin = self.env['mail.render.mixin'].with_context(**ctx)
        subject = RenderMixin._render_template(mail_template.subject, 'hr.appraisal.objective', self.ids, post_process=True)[self.id]
        body = RenderMixin._render_template(mail_template.body_html, 'hr.appraisal.objective', self.ids, post_process=True)[self.id]
        
        mail_values = {
            'email_from': self.env.user.email_formatted,
            'author_id': self.env.user.partner_id.id,
            'model': None,
            'res_id': None,
            'subject': subject,
            'body_html': body,
            'auto_delete': True,
            'email_to': self.employee_id.parent_id.work_email
        }
        activity= self.env['mail.mail'].sudo().create(mail_values)
        activity.send()
    
    
    @api.depends('employee_id')
    def _compute_work_locationn(self):
        for obj in self:
            obj.update({
                'work_location_id': obj.employee_id.work_location_id.id,
                'cwork_location_id': obj.employee_id.work_location_id.id,
                'department_id': obj.employee_id.department_id.id,
            })

    def  _compute_employee_company(self):
        for obj in self:
            if obj.employee_id:
                obj.update({
                    'company_id': obj.employee_id.company_id.id,
                })
    
    def unlink(self):
        for rec in self:
            if rec.state in ['confirm','waiting']:
                raise UserError(('Deletion is Not Allowed!'))
        return super(HrAppraisalObjective, self).unlink()
    
     
    @api.constrains('employee_id')
    def compute_readonly(self):
        for rec in self:
            if rec.state == 'confirm' and rec.env.user.has_group('de_appraisal_enhancement.group_allow_edit_objectives'):
                rec.readonly_status = 'make_editable'
            if rec.state == 'confirm' and not rec.env.user.has_group('de_appraisal_enhancement.group_allow_edit_objectives'):
                rec.readonly_status = 'make_readonly'
            else:
                rec.readonly_status = 'make_editable'
    
    @api.constrains('objective_year')
    def onchange_objective_year(self):
        if self.objective_year:
            if self.employee_id.id:
                appraisal_exists = self.search([('employee_id','=',self.employee_id.id),('objective_year','=',self.objective_year),('state','!=','draft')])
                if appraisal_exists:
                    raise UserError(('Objective Already exist for this year'))
            else:
                raise UserError(('First select the employee'))

    
    @api.model
    def create(self,vals):
        if vals['objective_year']:
            appraisal_exists = self.search([('state', 'not in', ['cancel','draft']),('employee_id','=',vals['employee_id']),('objective_year','=',vals['objective_year'])])
            if appraisal_exists:
                raise UserError(('Objective Already Exist for Selected Year'))
        result = super(HrAppraisalObjective, self).create(vals)
        return result


    def _create_appraisal_record_selected(self):
        employee_list = []
        for obj in self:
            employee_list.append(obj.employee_id.id) 
        uniq_emp_list = set(employee_list)    
        appraisal_plan = self.env['hr.appraisal.autoplan'].search([('target_year','=','2021')], limit=1)
        if appraisal_plan.run_date == fields.date.today():
            for record in uniq_emp_list:
                objective_ids = self.env['hr.appraisal.objective'].search([('employee_id', '=',record),('objective_year', '=','2021'),('is_posted','=',False)], limit=1)
                if objective_ids and objective_ids.is_posted==False:
                    employee_exist = self.env['hr.employee'].search([('id','=', record)], limit=1)
                    mid_start_date = appraisal_plan.mid_year_date
                    mid_deadline_date = mid_start_date + timedelta(days=10)
                    end_start_date = appraisal_plan.end_year_date
                    end_deadline_date = end_start_date + timedelta(days=10)
                    rec =  self.env['hr.appraisal.feedback'].create({
                        'name': record,
                        'performance_period': '2021',
                        'mid_year_date':mid_start_date,
                        'date_mid_deadline': mid_deadline_date,
                        'end_year_date': end_start_date,
                        'date_end_deadline': end_deadline_date,
                    })
                    objective_ids = self.env['hr.appraisal.objective'].search([('employee_id', '=',record),('objective_year', '=','2021'),('is_posted','=',False)], limit=1)
                    if objective_ids:
                        rec.update({
                        'training_need': objective_ids.traing_need,
                        })
                        if objective_ids.objective_lines:
                            for line in objective_ids.objective_lines:
                                self.env['hr.appraisal.feedback.objective.line'].create({
                                    'objective': line.objective,
                                    'obj_description': line.measuring_indicator,
                                    'weightage': line.weightage,
                                    'priority': line.priority if line.priority else 'low',
                                    'feedback_id': rec.id
                                })


                    value_ids = self.env['hr.appraisal.values'].search([('company_id','=',employee_exist.company_id.id)], order='company_id asc',limit=1)
                    if value_ids:
                        if value_ids.values_lines:
                            for line in value_ids.values_lines:
                                self.env['hr.appraisal.feedback.values.line'].create({
                                    'core_values': line.core_value,
                                    'core_description': line.description,
                                    'weightage': line.weightage,
                                    'priority': line.priority if line.priority else 'low',
                                    'feedback_id': rec.id})

                    objective_appraisee_ids = self.env['hr.appraisal.objective'].search([('employee_id', '=',record),('objective_year', '=','2021'),('is_posted','=',False)], limit=1)
                    if objective_ids:
                        if objective_ids.objective_lines:
                            for line in objective_ids.objective_lines:
                                self.env['hr.appraisal.feedback.objective.appraisee.line'].create({
                                    'objective': line.objective,
                                    'obj_description': line.measuring_indicator,
                                    'weightage': line.weightage,
                                    'priority': line.priority if line.priority else 'low',
                                    'feedback_id': rec.id
                                })
                    value_appraisee_ids = self.env['hr.appraisal.values'].search([('company_id','=',employee_exist.company_id.id)], order='company_id asc',limit=1)
                    if value_ids:
                        if value_ids.values_lines:
                            for line in value_ids.values_lines:
                                self.env['hr.appraisal.feedback.values.appraisee.line'].create({
                                    'core_values': line.core_value,
                                    'core_description': line.description,
                                    'weightage': line.weightage,
                                    'priority': line.priority if line.priority else 'low',
                                    'feedback_id': rec.id
                                })
                    objective_ids.update({
                        'is_posted': True
                    }) 


    
    @api.constrains('weightage')
    def limit_weightage(self):
        for rec in self:
            count = 0
            line_count = 0
            for line in rec.objective_lines:
                count = count + line.weightage
                line_count += 1
    
            rec.total_weightage = count

    @api.model
    def create(self,vals):
        res = super(HrAppraisalObjective, self).create(vals)
        if res.total_weightage > 100:
            raise UserError('Total Weightage must be equal 100')
        return res
    
    def write(self, vals):
        res = super(HrAppraisalObjective, self).write(vals)
        if self.total_weightage > 100:
            raise UserError('Total Weightage must be equal 100')
        return res
    
    
    def action_sent_review(self):
        for obj in self:
            line_count = 0
            for line in obj.objective_lines:
                line_count += 1
            if line_count < 3:
                raise UserError('At least 3 objectives require to Submit Objective Setting (Minimum=3, Maximum=8)')
            if line_count > 8:
                raise UserError('Maximum 8 objectives require to Submit Objective Setting (Minimum=3, Maximum=8)') 
            if obj.total_weightage != 100:
                raise UserError('Total Weightage must be equal 100')        
            obj.update({
                'state': 'waiting'
            })
            obj.action_send_mail()
        
    def action_reset(self):
        self.state = 'draft'     
        
    def action_submit(self):
        for obj in self:
            line_count = 0
            for line in obj.objective_lines:
                line_count += 1
            if line_count < 3:
                raise UserError('At least 3 objectives require to Confirm Objective Setting (Minimum=3, Maximum=8)')
            if line_count > 8:
                raise UserError('Maximum 8 objectives require to Confirm Objective Setting (Minimum=3, Maximum=8)') 
            if obj.total_weightage != 100:
                raise UserError('Total Weightage must be equal 100') 
            obj.update({
                    'state': 'confirm'
                })    
        
    
class HrAppraisalObjectiveline(models.Model):
    _name = 'hr.appraisal.objective.line'
    _description = 'Appraisal Objective Line'
    
    objective_id = fields.Many2one('hr.appraisal.objective')
    objective = fields.Char('Objective', required=True)
    description = fields.Char('Description', required=False)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ], string='Priority', index=True, copy=False)

    weightage = fields.Float(string='Weightage' , required=True)
    category_id = fields.Many2one('hr.objective.category', string='Category', required=True)
    status_id = fields.Many2one('hr.objective.status',  string='Status')
    measuring_indicator = fields.Char('Measuring Indicator')
    
    @api.onchange('weightage')
    def limit_weightage(self):
        if self.weightage:
            for rec in self:
                if rec.weightage > 100 or rec.weightage <1:
                    raise UserError('Weightage Cannot be greater than 100 or less than 1')
                
        
    
class ObjectiveCategories(models.Model):
    _name = 'hr.objective.category'
    _description= 'HR Objective Category'
    
    name = fields.Char(string='Description', required=True)
    
class ObjectiveStatus(models.Model):
    _name = 'hr.objective.status'
    _description= 'HR Objective Status'
    
    name = fields.Char(string='Description', required=True)    
    