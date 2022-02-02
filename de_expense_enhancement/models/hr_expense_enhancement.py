from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta




class HrExpense(models.Model):
    _inherit = 'hr.expense'

    claim_type_check = fields.Boolean(string='check', compute='_compute_claim_type')
    claim_type = fields.Selection([('funds_request', 'Funds Request'), ('re_imbursement', 'Re-imbursement Request')],
                                  string='Claim Type', default='re_imbursement')
    
    

    def _compute_claim_type(self):
        """
        To check selected Employee has Can Request For Fund Requests
        """
        if self.employee_id.can_request_funds_expense == True:
            self.claim_type_check = True
        else:
            self.claim_type_check = False

    @api.onchange('name')
    def onchange_claim(self):
        """
        To check selected Employee has Can Request For Fund Requests
        """
        if self.employee_id.can_request_funds_expense == True:
            self.claim_type_check = True
        else:
            self.claim_type_check = False

    @api.constrains('sub_category_id', 'employee_id', 'unit_amount', 'quantity', 'claim_type')
    def _constraints_claim_type(self):
        if self.sub_category_id.is_petty_cash == True and self.employee_id.can_request_petty_cash != True:
            raise UserError("You can't make claim for this " + str(self.sub_category_id.name))

        elif self.sub_category_id.is_petty_cash == True and self.employee_id.can_request_petty_cash == True:
                employee_period = int(self.employee_id.petty_cash_period)
                expense_period_date = date.today() - relativedelta(years=employee_period)
                employee_petty_cash_limit = self.employee_id.petty_cash_limit
                employee_expenses = self.env['hr.expense'].search(
                    [('sub_category_id', '=', self.sub_category_id.id), ('employee_id', '=', self.employee_id.id),
                     ('state', '!=', 'draft'),
                     ('state', '!=', 'refused')])
                sum = 0
                for expense in employee_expenses:
                    if ( expense.create_date.date() > expense_period_date and expense.create_date.date() <= date.today()):
                        sum = sum + expense.total_amount
                sum = round(sum, 2)
                sum_current = sum + self.total_amount
                if sum_current > employee_petty_cash_limit:
                    raise UserError(
                        "You have Already claimed " + str(
                            sum) + " against " + str(self.sub_category_id.name) + ". Your Limit is " + str(
                            employee_petty_cash_limit) + ". Cant Process expense request")

        if self.claim_type == 're_imbursement' and self.sub_category_id.is_petty_cash != True:
            flag = False
            limit = 0
            period = 0
            ora_unit = 'amount'
            for rec in self.employee_id.grade_designation.grade_line_ids:
                if self.sub_category_id.id == rec.expense_type.id:
                    flag = True
                    limit = rec.limit
                    ora_unit = rec.ora_unit
                    period = int(rec.period)
            expense_period_date = date.today() - relativedelta(years=period)
            if flag == False and self.sheet_id.exception!=True:
                raise UserError("You are not allowed to make Claim against the selected expense type")
            else:
                employee_expenses = self.env['hr.expense'].search(
                    [('sub_category_id', '=', self.sub_category_id.id), ('employee_id', '=', self.employee_id.id)
                        , ('state', '!=', 'draft'), ('state', '!=', 'refused'),
                     ('claim_type', '=', self.claim_type)])
                sum = 0
                for expense in employee_expenses:
                    if (
                            expense.create_date.date() > expense_period_date and expense.create_date.date() <= date.today()):
                        sum = sum + expense.total_amount
                sum = round(sum, 2)
                sum_current = sum + self.total_amount
                if sum_current > limit and ora_unit!='km' and self.sheet_id.exception!=True and self.sub_category_id.ora_category_id.is_amount_limit==True:
                    raise UserError(
                        "You have Already claimed " + str(
                            sum) + " against " + str(self.sub_category_id.name) + ". Your Limit is " + str(
                            limit) + ". Cant Process expense request")
                else:
                    pass
        elif self.claim_type == 'funds_request':
            if self.employee_id.can_request_funds_expense == False:
                raise UserError("You are not allowed to make Claim against the selected expense type")
            else:
                flag = False
                limit = 0
                period = 0
                for rec in self.employee_id.grade_designation.grade_line_ids:
                    if self.sub_category_id.id == rec.expense_type.id:
                        flag = True
                        limit = rec.funds_request_limit
                        period = int(rec.funds_request_period)
                expense_period_date = date.today() - relativedelta(years=period)
                if flag == False:
                    raise UserError("You are not allowed to make Claim against the selected expense type")
                else:
                    employee_expenses = self.env['hr.expense'].search(
                        [('sub_category_id', '=', self.sub_category_id.id), ('employee_id', '=', self.employee_id.id),
                         ('state', '!=', 'draft'),
                         ('state', '!=', 'refused'), ('claim_type', '=', self.claim_type)])
                    sum = 0
                    for expense in employee_expenses:
                        if (
                                expense.create_date.date() > expense_period_date and expense.create_date.date() <= date.today()):
                            sum = sum + expense.total_amount
                    sum = round(sum, 2)
                    sum_current = sum + self.total_amount

                    if sum_current > limit:
                        raise UserError(
                            "You Already have claimed " + str(sum) + " against " + str(
                                self.sub_category_id.name) + ". Your Limit is " + str(
                                limit) + ". Cant Process expense request")
                    else:
                        pass
