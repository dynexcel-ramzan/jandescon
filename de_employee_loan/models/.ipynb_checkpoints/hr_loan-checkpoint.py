# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Loan Request"



    def _compute_loan_amount(self):
        total_paid = 0.0
        for loan in self:
            for line in loan.loan_lines:
                if line.paid:
                    total_paid += line.amount
            balance_amount = loan.loan_amount - total_paid
            loan.total_amount = loan.loan_amount
            loan.balance_amount = balance_amount
            loan.total_paid_amount = total_paid

    name = fields.Char(string="Loan Name", default="/", readonly=True, help="Name of the loan")
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True, help="Date")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, help="Employee",)
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,
                                    string="Department", help="Employee")
    installment = fields.Integer(string="Duration(Months)", default=1, help="Number of installments")
    payment_date = fields.Date(string="Payment Start Date", required=True, default=fields.Date.today(), help="Date of "
                                                                                                             "the "
                                                                                                             "paymemt")
    loan_type_id = fields.Many2one('hr.loan.type', 'Loan Type', required=True, help="Loan",)

    loan_lines = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", index=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True, help="Company",
                                 default=lambda self: self.env.user.company_id,
                                 states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position",
                                   help="Job position")
    loan_amount = fields.Float(string="Loan Amount", required=True, help="Loan amount")
    total_amount = fields.Float(string="Total Amount", store=True, readonly=True, compute='_compute_loan_amount',
                                help="Total loan amount")
    balance_amount = fields.Float(string="Balance Amount", store=True, compute='_compute_loan_amount', help="Balance amount")
    total_paid_amount = fields.Float(string="Total Paid Amount", store=True, compute='_compute_loan_amount',
                                     help="Total paid amount")
    
    
    proof_line_ids = fields.One2many('hr.employee.loan.proof', 'proof_loan_id', string="Proof Line")
    policy_line_ids = fields.One2many('hr.employee.loan.policy.line', 'policy_loan_id', string="Policy Line", index=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Submitted'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )
    
    
     
    @api.constrains('installment')
    def onchange_installment(self):
        if self.installment:
            if self.installment  > self.loan_type_id.installment:
                raise ValidationError(_("You are not allow to Enter Installment More than "+ ' ' + str(self.loan_type_id.installment) + ' !'))
           
    
    @api.constrains('name')
    def _check_name(self):
        if self.name:
            policy_gap_between_loan = 1
            for policy in self.policy_line_ids:
                if policy.policy_type == 'gap_between_date':
                    policy_gap_between_loan = policy.gap_value
            existing_loan = self.env['hr.loan'].search([('employee_id','=', self.employee_id.id),('state','in', ['waiting_approval_1','approve'])],order='date desc', limit=1)
            if existing_loan:
                current_year_date = fields.date.today()
                existing_loan_year_date = fields.date.today()
                existing_loan_year = existing_loan_year_date.year
                current_year = current_year_date.year
                if existing_loan: 
                    existing_loan_year = existing_loan.date.year
                    current_year = self.date.year
                loan_gap = current_year - existing_loan_year 
                if loan_gap >= policy_gap_between_loan:
                    pass
                else:
                    raise ValidationError(('You have already a Loan request with the sequence # ' +str(existing_loan.name)+ ' on ' + str(existing_loan.date)+' ' + str(loan_gap) +' now you can avail loan after '+ str(policy_gap_between_loan)+' year of you first loan installment end' ))

                                    
    
    
    
    @api.constrains('loan_amount')
    def onchange_amount(self):
        if self.policy_line_ids:
            for policy in self.policy_line_ids:
                if policy.policy_type == 'max_loan' and policy.value_type== 'fix_amount':
                    max_amount = 0
                    if policy.policy_type == 'max_loan' and policy.value_type== 'fix_amount':
                        max_amount =  policy.value 

                    if self.loan_amount > max_amount:
                        raise ValidationError(_("You are not allow to Enter Loan Amount More than "+ ' ' + str(max_amount) + ' !'))
                        
                elif policy.policy_type == 'max_loan' and policy.value_type== 'percent':
                    max_amount = 0
                    if policy.policy_type == 'max_loan' and policy.value_type== 'percent':
                        contract = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','=','open')])
                        max_amount =  ((policy.value * contract.wage) /100)

                    if self.loan_amount > max_amount:
                        raise ValidationError(_("You are not allow to Enter Loan Amount More than "+ ' ' + str(max_amount) + ' !'))        
           
                        
                    

                
            
        
    
    
    @api.constrains('employee_id')
    def _check_employee(self):        
        if self.employee_id:
            for line in self.policy_line_ids:
                line.unlink()
            policy_data = []
            policy_qualification = 0
            loan_policy= self.env['hr.loan.policy'].search([])
            for policy in loan_policy:
                policy_qualification = 0
                if policy.employee_type == self.employee_id.emp_type:
                    if policy.policy_type == 'qualify_period':
                        policy_qualification = policy.gap_value
                        
                    policy_data.append((0,0,{
                                    'name' : policy.name,
                                    'policy_type' : policy.policy_type,
                                    'value_type' : policy.value_type,
                                    'value' : policy.value,
                                    'gap_type' : policy.gap_type,
                                    'gap_value' :  policy.gap_value,
                                    'policy_loan_id': self.id,
                                }))    
                
                elif policy.employee_ids:
                    for employee in policy.employee_ids:
                        if employee.id == self.employee_id.id:
                            if policy.policy_type == 'gap_between_date':
                                policy_gap_between_loan = policy.gap_value
                            if policy.policy_type == 'qualify_period':
                                policy_qualification = policy.gap_value
                        
                            policy_data.append((0,0,{
                                    'name' : policy.name,
                                    'policy_type' : policy.policy_type,
                                    'value_type' : policy.value_type,
                                    'value' : policy.value,
                                    'gap_type' : policy.gap_type,
                                    'gap_value' :  policy.gap_value,
                                    'policy_loan_id': self.id,
                                }))
                    
                        
            self.policy_line_ids =  policy_data 
            
            employee_service = 365 * policy_qualification
            total_days = 0
            employee_record = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
            for employee in employee_record:
                if not employee.date:
                    raise ValidationError(('Date of Joining is Missing'))
                delta = self.payment_date - employee.date
                total_days = delta.days
                

            if employee_service < total_days:
                pass
            else:
                raise ValidationError(('You can avail Loan after '+ str(policy_qualification)+ ' Year Service' ))
                
            for emp in employee_record:
                if self.loan_type_id.compansation == 'normal':                    
                    if emp.grade_type.name != self.loan_type_id.grade_type_id.name:
                        raise ValidationError(('You are not Eligible, Only Management Staff Avail This Facility'))  

                    elif emp.emp_type != self.loan_type_id.employee_type:
                        raise ValidationError(('You are not Eligible, Only Permanent & Contractual Staff Avail This Facility')) 
            
            
    
    
    
    @api.constrains('loan_type_id')
    def _check_loan_type(self):        
        if self.loan_type_id:
            proof_data = []
            for proof_line in self.proof_line_ids:
                proof_line.unlink()
            
            if self.loan_type_id.compansation == 'normal':
                if self.employee_id.grade_type.name != self.loan_type_id.grade_type_id.name:
                    raise ValidationError(('You are not Eligible, Only Management Staff Avail This Facility'))  

                elif self.employee_id.emp_type != self.loan_type_id.employee_type:
                    raise ValidationError(('You are not Eligible, Only Permanent & Contractual Staff Avail This Facility')) 
            else:
                
                if self.loan_type_id.employee_ids:                    
                    if self.employee_id in self.loan_type_id.employee_ids:
                            pass
                    else:
                        raise ValidationError(_("You are not allow to Request Loan for this Loan Type. Please Select other Loan Type!"))

                
            for proof in self.loan_type_id.loan_type_proof_ids:    
                proof_data.append((0,0,{
                    'name' : proof.name,
                    'mandatory': proof.mandatory, 
                }))
            self.proof_line_ids = proof_data
            
            
   
                

                
               
            
    
    

    @api.model
    def create(self, values):
        loan_count = self.env['hr.loan'].search_count(
            [('employee_id', '=', values['employee_id']), ('state', '=', 'approve'),
             ('balance_amount', '!=', 0)])
        
            
        if loan_count:
            raise ValidationError(_("The employee has already a pending installment"))
        else:
            values['name'] = self.env['ir.sequence'].get('hr.loan.seq') or ' '
            res = super(HrLoan, self).create(values)
            return res
        
        

    def compute_installment(self):
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        for loan in self:
            loan.loan_lines.unlink()
            date_start = datetime.strptime(str(loan.payment_date), '%Y-%m-%d')
            amount = loan.loan_amount / loan.installment
            for i in range(1, loan.installment + 1):
                self.env['hr.loan.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id})
                date_start = date_start + relativedelta(months=1)
            loan._compute_loan_amount()
        return True

    def action_refuse(self):
        return self.write({'state': 'refuse'})

    def action_submit(self):
        self.write({'state': 'waiting_approval_1'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_approve(self):
        for data in self:
            data.compute_installment()
            if not data.loan_lines:
                raise ValidationError(_("Please Compute installment"))
            else:
                self.write({'state': 'approve'})

    def unlink(self):
        for loan in self:
            if loan.state not in ('draft', 'cancel'):
                raise ValidationError(
                    'You cannot delete a loan which is not in draft or cancelled state')
        return super(HrLoan, self).unlink()


class InstallmentLine(models.Model):
    _name = "hr.loan.line"
    _description = "Installment Line"

    date = fields.Date(string="Payment Date", required=True, help="Date of the payment")
    employee_id = fields.Many2one('hr.employee', string="Employee", help="Employee")
    amount = fields.Float(string="Amount", required=True, help="Amount")
    paid = fields.Boolean(string="Paid", help="Paid")
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.", help="Loan")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.", help="Payslip")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_employee_loans(self):
        """This compute the loan amount and total loans count of an employee.
            """
        self.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', self.id)])

    loan_count = fields.Integer(string="Loan Count", compute='_compute_employee_loans')
    
    
    def action_view_loan(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'name': 'Loan',
            'domain': [('employee_id','=', self.id)],
            'target': 'current',
            'res_model': 'hr.loan',
            'view_mode': 'tree,form',
        }

    
    
class HrEmployeeLoanProof(models.Model):
    _name = "hr.employee.loan.proof"
    _description = "Hr Employee Loan Proof"

    name = fields.Char(string="Name", readonly=True, help="Date of the payment")
    mandatory = fields.Boolean(string="Required", readonly=True, help="Employee")
    proof_loan_id = fields.Many2one('hr.loan', string="Loan", help="Loan") 
    attachment_id = fields.Many2many('ir.attachment', relation="files_rel_attachted",
                                            column1="doc_id",
                                            column2="attachment_id",
                                            string="Attachment")
  


class HrEmployeeLoanPolicy(models.Model):
    _name = "hr.employee.loan.policy.line"
    _description = "Hr Employee Loan Policy"

    name = fields.Char(string="Name", required=True, help="Name for Policy")
    policy_type = fields.Selection([
                             ('max_loan','Max loan amount'),
                             ('gap_between_date','Gap between two loans'),
                             ('qualify_period','Qualifying Period'), 
                            ],  default = 'max_loan', string="Policy Type")
    
    value_type = fields.Selection([
                             ('fix_amount', 'Fix Amount'),
                             ('percent', 'Percentage'),
                            ],  default = 'fix_amount', string="Basis")
    
    value = fields.Float(string="Value")
    
    gap_type = fields.Selection([
                             ('month', 'Month'),
                             ('year', 'Year'),
                            ],  default = 'year', string="By")
    
    gap_value = fields.Integer(string="Value")
    policy_loan_id = fields.Many2one('hr.loan', string="Loan", help="Loan")

    