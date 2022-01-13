# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime
import base64

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips, ResultRules
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval

class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    loan_line_id = fields.Many2one('hr.loan.line', string="Loan Installment", help="Loan installment")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    
    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
#         if self.employee_id:
#             raise UserError(("test"))
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        contracts = []
        self.company_id = employee.company_id
        if not self.contract_id or self.employee_id != self.contract_id.employee_id: # Add a default contract if not already defined
            contracts = employee._get_contracts(date_from, date_to)

            if not contracts or not contracts[0].structure_type_id.default_struct_id:
                self.contract_id = False
                self.struct_id = False
                return
            self.contract_id = contracts[0]
            self.struct_id = contracts[0].structure_type_id.default_struct_id

        lang = employee.sudo().address_home_id.lang or self.env.user.lang
        context = {'lang': lang}
        payslip_name = self.struct_id.payslip_name or _('Salary Slip')
        del context

        self.name = '%s - %s - %s' % (
            payslip_name,
            self.employee_id.name or '',
            format_date(self.env, self.date_from, date_format="MMMM y", lang_code=lang)
        )

        if date_to > date_utils.end_of(fields.Date.today(), 'month'):
            self.warning_message = _(
                "This payslip can be erroneous! Work entries may not be generated for the period from %(start)s to %(end)s.",
                start=date_utils.add(date_utils.end_of(fields.Date.today(), 'month'), days=1),
                end=date_to,
            )
        else:
            self.warning_message = False
            
        
        self.worked_days_line_ids = self._get_new_worked_days_lines()
        if self.contract_id:
            contracts = self.contract_id
            employee = self.employee_id
            date_from = self.date_from
            date_to = self.date_to
            data = []
            other_inputs = self.env['hr.payslip.input.type'].search([])
            contract_obj = self.env['hr.contract']
            emp_id = contract_obj.browse(contracts[0].id).employee_id
            lon_obj = self.env['hr.loan'].search([('employee_id', '=', emp_id.id), ('state', '=', 'approve')])
            for loan in lon_obj:
                for loan_line in loan.loan_lines:
                    if date_from <= loan_line.date <= date_to and not loan_line.paid:
                        for result in other_inputs:
                            if result.code == 'LOAN':  
                                data.append((0,0,{
                                'payslip_id': self.id,
                                'sequence': 1,
                                'code': result.code,
                                'contract_id': self.contract_id.id,
                                'input_type_id': result.id,
                                'amount': loan_line.amount,
                                 'loan_line_id': loan_line.id   
                                }))    
        self.input_line_ids = data
            
            
    def compute_sheet(self):
        for payslip in self: 
            for other_input in payslip.input_line_ids:
                if other_input.code=='LOAN':
                    other_input.unlink()
            if payslip.contract_id:
                contracts = payslip.contract_id
                employee = payslip.employee_id
                date_from = payslip.date_from
                date_to = payslip.date_to
                data = []
                other_inputs = self.env['hr.payslip.input.type'].search([])
                contract_obj = self.env['hr.contract']
                emp_id = contract_obj.browse(contracts[0].id).employee_id
                lon_obj = self.env['hr.loan'].search([('employee_id', '=', emp_id.id), ('state', '=', 'approve')])
                for loan in lon_obj:
                    for loan_line in loan.loan_lines:
                        if date_from <= loan_line.date <= date_to and not loan_line.paid:
                            for result in other_inputs:
                                if result.code == 'LOAN':  
                                    data.append((0,0,{
                                      'payslip_id': payslip.id,
                                      'sequence': 1,
                                      'code': result.code,
                                      'contract_id': payslip.contract_id.id,
                                      'input_type_id': result.id,
                                      'amount': loan_line.amount,
                                      'loan_line_id': loan_line.id   
                                    }))    
            payslip.input_line_ids = data
        res = super(HrPayslip, self).compute_sheet()

        return res
   


    def action_payslip_done(self):
        for payslip in self: 
            for line in payslip.input_line_ids:
                if line.loan_line_id:
                    line.loan_line_id.paid = True
                    line.loan_line_id.loan_id._compute_loan_amount()
        return super(HrPayslip, self).action_payslip_done()
