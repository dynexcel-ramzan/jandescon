# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError


class EmployeeEnhancement(models.Model):
    _inherit = 'hr.employee'

    emp_number = fields.Char('Employee Number')
    emp_status = fields.Char('Employee Status')
    emp_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('contractor', 'Contractor'),
        ('freelancer', 'Freelancer'),
        ('inter', 'Intern'),
        ('part_time', 'Part Time'),
        ('project_based', 'Project Based Hiring'),
        ('outsource', 'Outsource'),
        ], string='Employee Type', index=True, copy=False, default='permanent', track_visibility='onchange')
    section = fields.Char('Section')
    father_name = fields.Char("Father's Name")
    grade_type = fields.Many2one('grade.type')
    grade_designation = fields.Many2one('grade.designation')
    date = fields.Date('Date of Joining')
    probation_period = fields.Selection([
        ('1', '1 Month'),
        ('2', '2 Months'),
        ('3', '3 Months'),
        ('4', '4 Months'),
        ('5', '5 Months'),
        ('6', '6 Months'),
        ('9', '9 Months'),
        ('12', '12 Months'),
        ], string='Probation Period', index=True, copy=False, default='1', track_visibility='onchange')

    confirm_date = fields.Date('Confirmation Date', compute='compute_confirmation_date')
    contract_expiry = fields.Date("Contract Expiry", compute='compute_contract_date')# Need To confirm
    cnic = fields.Char('CNIC', size=13)

    def compute_contract_date(self):
        for record in self:
            rec = self.env['hr.contract'].search([('employee_id', '=', record.id), ('state', '=', 'open')])
            record.contract_expiry = rec.date_end

    @api.constrains('cnic')
    def compute_cnic(self):
    	if self.cnic:
    		if len(self.cnic) < 13 :
    			raise UserError(('CNIC No is invalid'))
    		if not self.cnic.isdigit():
    			raise UserError(('CNIC No is invalid'))

    blood_group = fields.Selection([
        ('a+', 'A+'),
        ('a-', 'A-'),
        ('b+', 'B+'),
        ('b-', 'B-'),
        ('o+', 'O+'),
        ('o-', 'O-'),
        ('ab+', 'AB+'),
        ('ab-', 'AB-'),
        ], string='Blood Group', index=True, copy=False, default='a+', track_visibility='onchange')
    fac_deduction = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ], string='FAC Deduction Applicable', index=True, copy=False, default='yes', track_visibility='onchange')
    fac_deduction_percentage = fields.Char('FAC Deduction Percentage(%)', size=3)
    is_consultant = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ], string='Is Consultant', index=True, copy=False, default='yes', track_visibility='onchange')
    tax_rate = fields.Float('Consultant Tax Rate')
    resigned_date = fields.Date("Resigned Date")
    resign_type = fields.Char("Resign Type")
    resigned_remarks = fields.Char("Resigned Remarks")
    resign_reason = fields.Char("Resign Reason")
    religion = fields.Selection([
        ('islam', 'Islam'),
        ('christianity', 'Christianity'),
        ('judism', 'Judism'),
        ('buddhism', 'Buddhism'),
        ('hindu', 'Hinduism'),
        ('other', 'Other'),
        ], string='Religion', index=True, copy=False, default='islam', track_visibility='onchange')
    ntn = fields.Char("NTN", size=8)
    temporary_address = fields.Char('Temporary Address')
    pf_member = fields.Selection([
        ('no', 'No'),
        ('yes_with', 'Yes with Interest'),
        ('yes_without', 'Yes w/o Interest'),
        ], string='PF Member', index=True, copy=False, default='no', track_visibility='onchange')
    pf_trust = fields.Char('PF Trust')
    pf_effec_date = fields.Date('PF Effective Date')
    ss_entitled = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ], string='SS Entitled', index=True, copy=False, default='yes', track_visibility='onchange')
    ss_number = fields.Char('SS Number')
    union_fund = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ], string='Union Fund Entitled', index=True, copy=False, default='yes', track_visibility='onchange')
    eobi_member = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ], string='EOBI member', index=True, copy=False, default='no', track_visibility='onchange')
    union_fund_amount = fields.Float('Union Fund Amount')
    ot_allowed = fields.Boolean('OT Allowed')
    gratuity = fields.Boolean('Has Gratuity')
    stop_salary = fields.Boolean('Stop Salary')
    eobi_number = fields.Char('EOBI Number')
    eobi_registration_date = fields.Date('EOBI Registration Date')
    wps = fields.Char('WPS')
    ipl_variable = fields.Char('IPL Variable Cost')
    # cost_center_information_line = fields.One2many('cost.information.line', 'employee_id')
    reason_to_leave = fields.Char('Reason To Leave')
    salary = fields.Float('Salary')
    # FIXME: ###############################
    institute = fields.Char('Institute')
    project_lines = fields.One2many('employee.project.line', 'employee_id')
    benefit_lines = fields.One2many('employee.benefit.line', 'employee_id')
    asset_lines = fields.One2many('employee.asset.line', 'employee_id')

    def compute_confirmation_date(self):
        for date_rec in self:
            if date_rec.date:
                prob_date = date_rec.probation_period
                date = date_rec.date + relativedelta(months=int(prob_date))
            else:
                date = ''
            date_rec.confirm_date = date




class EmployeeAssets(models.Model):
    _name = 'employee.asset'

    name = fields.Char('Asset Name')
    life_span = fields.Char('Life Span')
    value = fields.Float('Value')
    code = fields.Char('Asset Code')


class EmployeeAssetsLine(models.Model):
    _name = 'employee.asset.line'

    employee_id = fields.Many2one('hr.employee')
    asset_id = fields.Many2one('employee.asset')
    issue_date = fields.Date('Issue Date')
    description = fields.Text('Description')
    estimated_life_span = fields.Char('Estimated Life Span', related='asset_id.life_span')
    recovery_date = fields.Date('Recovery Date')


class EmployeeProjectLine(models.Model):
    _name = 'employee.project.line'

    employee_id = fields.Many2one('hr.employee')
    name = fields.Char('Project')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    location = fields.Char('Location')
    period = fields.Char('Period', compute='compute_period')  # compute period

    def compute_period(self):
        if self.start_date and self.end_date:
            # date = self.end_date - self.start_date
            rdelta = relativedelta(self.end_date, self.start_date)

        # date = date.strftime("%d/%m/%Y")

            if rdelta.days > 0 and rdelta.months > 0:
                result = str(rdelta.months) + " Months " + str(rdelta.days) + " Days"
            elif rdelta.days == 0:
                result = str(rdelta.months) + " Months"
            elif rdelta.months == 0:
                result = str(rdelta.days) + " Days"
        else:
            result = ''
        self.period = result

class EmployeeBenefitLine(models.Model):
    _name = 'employee.benefit.line'

    employee_id = fields.Many2one('hr.employee')
    name = fields.Char('Description')
    start_date = fields.Date('Start Date')
    benefit_remarks = fields.Char('Remarks')
    benefit_amount = fields.Integer('Amount')
    benefit_description = fields.Selection([
        ('car', 'Car'),
        ('fleet', 'Fleet Card'),
        ('mobile', 'Mobile'),
        ], string='Benefit', index=True, copy=False, default='car', track_visibility='onchange')


class GradeType(models.Model):
    _name = 'grade.type'

    name = fields.Char('Grade Type')


class GradeDesignation(models.Model):
    _name = 'grade.designation'

    name = fields.Char('Grade Designation')




class CostCenterInformations(models.Model):
    _inherit = 'hr.contract'
    
    expense_account = fields.Selection([
        ('1', 'Operating Expenses'),
        ('2', 'Factory Overheads'),
        ('3', 'Marketing Expenses'),
        ], string='Expense Head', index=True, copy=False, default='1', track_visibility='onchange')
    cost_center_information_line = fields.One2many('cost.information.line','contract_id',string='Cost Center Lines')
    total_percentage = fields.Float('Total Percentage', compute = 'limit_total_percentage')


#     @api.constrains('total_percentage')
    def limit_total_percentage(self):
        for rec in self:
            count = 0
            for line in rec. cost_center_information_line:
                count = count + line.percentage_charged
            rec.total_percentage = count

    @api.model
    def create(self,vals):
        res = super(CostCenterInformations, self).create(vals)
        if self.cost_center_information_line.cost_center:
        	if res.total_percentage != 100:
        		raise UserError('Total Percentage must be equal 100')
        return res
    
    def write(self, vals):
        res = super(CostCenterInformations, self).write(vals)
        if self.cost_center_information_line.cost_center:
        	if self.total_percentage != 100:
        		raise UserError('Total Percentage must be equal 100')
        return res


class CostCenterInformation(models.Model):
    _name = 'cost.information.line'

    contract_id = fields.Many2one('hr.contract')
    employee_id = fields.Many2one('hr.employee')
    cost_center = fields.Many2one('account.analytic.account')
    percentage_charged = fields.Float('Percentage Charged')

    @api.onchange('percentage_charged')
    def limit_percentage_charged(self):
        if self.percentage_charged:
            for rec in self:
                if rec.percentage_charged > 100 or rec.percentage_charged <1:
                    raise UserError('Percentage Charged Cannot be greater than 100 or less than 1')