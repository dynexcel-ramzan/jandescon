# -*- coding: utf-8 -*-
import time
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import except_orm
from odoo import exceptions
from odoo.exceptions import UserError, ValidationError

class SalaryAdvancePayment(models.Model):
    _name = "salary.advance"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', readonly=True, select=True, default=lambda self: 'Adv/')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date = fields.Date(string='Date', required=True, default=lambda self: fields.Date.today())
    reason = fields.Text(string='Reason')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    advance = fields.Float(string='Advance', required=True)
    payment_method = fields.Many2one('account.journal', string='Payment Method')
    exceed_condition = fields.Boolean(string='Exceed than maximum',
                                      help="The Advance is greater than the maximum percentage in salary structure")
    department = fields.Many2one('hr.department', string='Department', related='employee_id.department_id')
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submitted'),
                              ('waiting_approval', 'Waiting Approval'),
                              ('approve', 'Approved'),
                              ('cancel', 'Cancelled'),
                              ('reject', 'Rejected')], string='Status', default='draft', track_visibility='onchange')
    debit = fields.Many2one('account.account', string='Debit Account')
    credit = fields.Many2one('account.account', string='Credit Account')
    journal = fields.Many2one('account.journal', string='Journal')
    employee_contract_id = fields.Many2one('hr.contract', string='Contract')
    service_time = fields.Integer(string='Service Time')
    crnt_year = fields.Integer(string="Current Year", default=datetime.now().year)
    
    
    @api.constrains('employee_id')
    def onchange_employee(self):
        total_days = 0
        employee_record = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
        for employee in employee_record:
            if employee.date and self.date: 
            	delta = employee.date - self.date
            	total_days = abs(delta.days)
        self.service_time = total_days
        if total_days < 730:
            raise UserError(('You Cannot Avail This Facility, Your Service Period is Less Than Two Years'))            
        contract_id = self.env['hr.contract'].search([('employee_id','=', self.employee_id.id),('state','=','open')], limit=1)
        
        if contract_id and contract_id.state == 'open':
            self.employee_contract_id = contract_id.id
        else:
            self.employee_contract_id = None
        salary_advance_search = self.env['salary.advance'].search([('employee_id', '=', self.employee_id.id),('state', 'in',( 'approve','waiting_approval','submit'))] )
        current_year = datetime.strptime(str(self.date), '%Y-%m-%d').date().year
        for each_advance in salary_advance_search:
            existing_year = datetime.strptime(str(each_advance.date), '%Y-%m-%d').date().year

            if current_year == existing_year:
                raise UserError(('Error!', 'Advance can be requested once in a Year'))
                
        for emp in self.employee_id:
            if emp.grade_type.name != 'Management':
                raise UserError(('You are not Eligible, Only Management Staff Avail This Facility'))  

            elif emp.emp_type != 'permanent' and emp.emp_type != 'contractor':
                raise UserError(('You are not Eligible, Only Permanent & Contractual Staff Avail This Facility'))          

    


            
    @api.constrains('advance')
    def _check_advances(self):
        if self.advance:
            adv = self.advance
            amt = (self.employee_contract_id.structure_type_id.max_percent * self.employee_contract_id.wage) / 100
            if adv > amt and not self.exceed_condition:
                raise UserError(('Error!', 'Advance amount is greater than allotted. You are only allow to enter Amount '+str(amt)))

        
        
        
        
        


    def unlink(self):
        if any(self.filtered(lambda loan: loan.state not in ('draft', 'cancel'))):
            raise UserError(_('You cannot delete a Loan which is not draft or cancelled!'))
        return super(SalaryAdvancePayment, self).unlink()
    

    
    

            
            
    
    def onchange_employee_id(self, employee_id,employee_contract_id):
        if employee_id:
            employee_obj = self.env['hr.employee'].browse(employee_id)
            department_id = employee_obj.department_id.id
            employee_contract_id = employee_obj.contract_id.id
            domain = [('employee_id', '=', employee_id)]
            return {'value': {'department': department_id,'employee_contract_id':employee_contract_id}, 'domain': {
                        'employee_contract_id': domain,
                    }}

    @api.onchange('company_id')
    def onchange_company_id(self):
        company = self.company_id
        domain = [('company_id.id', '=', company.id)]
        result = {
            'domain': {
                'journal': domain,
            },

        }
        return result

    def submit_to_manager(self):
        self.state = 'submit'

    def cancel(self):
        self.state = 'cancel'

    def action_refuse(self):
        self.state = 'reject'

    @api.model
    def create(self, vals):
            
        vals['name'] = self.env['ir.sequence'].get('salary.advance.seq') or ' '
        res_id = super(SalaryAdvancePayment, self).create(vals)
        return res_id

    def approve_request(self):
        """This Approve the employee salary advance request.
                   """
        emp_obj = self.env['hr.employee']
        address = emp_obj.browse([self.employee_id.id]).address_home_id

        salary_advance_search = self.search([('employee_id', '=', self.employee_id.id), ('id', '!=', self.id),
                                             ('state', '=', 'approve')])
        current_month = datetime.strptime(str(self.date), '%Y-%m-%d').date().month
        for each_advance in salary_advance_search:
            existing_month = datetime.strptime(str(each_advance.date), '%Y-%m-%d').date().month
            if current_month == existing_month:
                raise UserError(('Error!', 'Advance can be requested once in a month'))
                
        salary_advance_search = self.search([('employee_id', '=', self.employee_id.id), ('id', '!=', self.id), ('id', '!=', self.id),
                                             ('state', '=', 'approve')])
        current_year = datetime.strptime(str(self.date), '%Y-%m-%d').date().year
        for each_advance in salary_advance_search:
            existing_year = datetime.strptime(str(each_advance.date), '%Y-%m-%d').date().year

            if current_year == existing_year:
                raise UserError('Error!', 'Advance can be requested once in a Year')   
        
        if not self.employee_id.contract_id:
            raise UserError(('Error!', 'Define a contract for the employee'))
        struct_id = self.employee_id.contract_id.structure_type_id
        contract = self.env['hr.contract'].search([('state','=','open'),('employee_id','=',self.employee_id.id)])
        if(self.employee_contract_id.id == False):
            self.employee_contract_id = contract
        if not struct_id.max_percent or not struct_id.advance_date:
            raise UserError(('Error!', 'Max percentage or advance days are not provided in Contract'))
        adv = self.advance
        amt = (self.employee_contract_id.structure_type_id.max_percent * self.employee_contract_id.wage) / 100
        if adv > amt and not self.exceed_condition:
            raise UserError(('Error!', 'Advance amount is greater than allotted'))

        if not self.advance:
            raise UserError(('Warning', 'You must Enter the Salary Advance amount'))
        payslip_obj = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id),
                                                     ('state', '=', 'done'), ('date_from', '<=', self.date),
                                                     ('date_to', '>=', self.date)])
        if payslip_obj:
            raise UserError(('Warning', "This month salary already calculated"))

        for slip in self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id)]):
            slip_moth = datetime.strptime(str(slip.date_from), '%Y-%m-%d').date().month
            if current_month == slip_moth + 1:
                slip_day = datetime.strptime(str(slip.date_from), '%Y-%m-%d').date().day
                current_day = datetime.strptime(str(self.date), '%Y-%m-%d').date().day
                if current_day - slip_day < struct_id.advance_date:
                    raise exceptions.Warning(
                        _('Request can be done after "%s" Days From prevoius month salary') % struct_id.advance_date)
        self.state = 'waiting_approval'

    def action_approve(self):
        """This Approve the employee salary advance request from accounting department.
                   """
        emp_obj = self.env['hr.employee']
        address = emp_obj.browse([self.employee_id.id]).address_home_id

        salary_advance_search = self.search([('employee_id', '=', self.employee_id.id), ('id', '!=', self.id),
                                             ('state', '=', 'approve')])
        current_month = datetime.strptime(str(self.date), '%Y-%m-%d').date().month
        for each_advance in salary_advance_search:
            existing_month = datetime.strptime(str(each_advance.date), '%Y-%m-%d').date().month
            if current_month == existing_month:
                raise UserError(('Error!', 'Advance can be requested once in a month'))
                
        salary_advance_search = self.search([('employee_id', '=', self.employee_id.id), ('id', '!=', self.id), ('id', '!=', self.id),
                                             ('state', '=', 'approve')])
        current_year = datetime.strptime(str(self.date), '%Y-%m-%d').date().year
        for each_advance in salary_advance_search:
            existing_year = datetime.strptime(str(each_advance.date), '%Y-%m-%d').date().year

            if current_year == existing_year:
                raise UserError('Error!', 'Advance can be requested once in a Year')   
        
        if not self.employee_id.contract_id:
            raise UserError(('Error!', 'Define a contract for the employee'))
        struct_id = self.employee_id.contract_id.structure_type_id
        contract = self.env['hr.contract'].search([('state','=','open'),('employee_id','=',self.employee_id.id)])
        if(self.employee_contract_id.id == False):
            self.employee_contract_id = contract
        if not struct_id.max_percent or not struct_id.advance_date:
            raise UserError(('Error!', 'Max percentage or advance days are not provided in Contract'))
        adv = self.advance
        amt = (self.employee_contract_id.structure_type_id.max_percent * self.employee_contract_id.wage) / 100
        if adv > amt and not self.exceed_condition:
            raise UserError(('Error!', 'Advance amount is greater than allotted'))

        if not self.advance:
            raise UserError(('Warning', 'You must Enter the Salary Advance amount'))
        payslip_obj = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id),
                                                     ('state', '=', 'done'), ('date_from', '<=', self.date),
                                                     ('date_to', '>=', self.date)])
        if payslip_obj:
            raise UserError(('Warning', "This month salary already calculated"))

        for slip in self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id)]):
            slip_moth = datetime.strptime(str(slip.date_from), '%Y-%m-%d').date().month
            if current_month == slip_moth + 1:
                slip_day = datetime.strptime(str(slip.date_from), '%Y-%m-%d').date().day
                current_day = datetime.strptime(str(self.date), '%Y-%m-%d').date().day
                if current_day - slip_day < struct_id.advance_date:
                    raise exceptions.Warning(
                        _('Request can be done after "%s" Days From prevoius month salary') % struct_id.advance_date)
        if not self.advance:
            raise UserError(('Warning', 'You must Enter the Salary Advance amount'))


        self.state = 'approve'
        return True
