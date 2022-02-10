from odoo import fields, models, api, _
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import date, datetime, timedelta


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    probation_leaves_allocated = fields.Boolean(string="Probation Leaves Allocated")
    pro_rate_leaves_allocated = fields.Boolean(string="Pro-rate Leaves Allocated")
    pro_rate_annual_leaves_allocated = fields.Boolean(string="Pro-rate Annual Leaves allocated")

    def schedular_probation(self):
        """
        Schedular For
        Time-Off: Probation Leave Allocation
        """
        current_date = date.today()
        employees_id = self.env['hr.employee'].search([])
        # to search Timeoff For Allocated During Probation and Current Target Year
        for employee in employees_id:
            time_off_for_probation = self.env['hr.leave.type'].search(
                [('allocated_during_probation', '=', True), ('fiscal_year', '=', current_date.year)
                    , ('company_id', '=', employee.company_id.id)])
            if employee.date and time_off_for_probation:
                if employee.date.year == current_date.year:
                    
                    if employee.emp_type == 'permanent' or employee.emp_type == 'contractor':
                        if employee.probation_leaves_allocated == False:
                            for timeoff in time_off_for_probation:
                                temp = ''
                                if timeoff.request_unit == 'day':
                                    temp = 'days'
                                elif timeoff.request_unit == 'hour':
                                    temp = 'hours'
                                pre_month=(fields.date.today().month - employee.date.month)
                                
                                vals = {
                                        'name': 'Probation Allocation For ' + employee.name,
                                        'holiday_status_id': timeoff.id,
                                        'allocation_type': 'accrual',
                                        'holiday_type': 'employee',  # get from Selection
                                        'employee_id': employee.id,
                                        'date_from': employee.date,  # Start Date
                                        'date_to': employee.confirm_date,  # Run Untill
                                        'number_per_interval': 0.83,
                                        'unit_per_interval': temp,
                                        'number_of_days': 0,
                                        'interval_number': 30,
                                        'interval_unit': 'days',
                                }
                                extra_month = 30 * pre_month
                                next_execution_date = employee.date + timedelta(extra_month)
                                if next_execution_date < fields.date.today() :
                                    next_execution_date = next_execution_date + timedelta(30) 
                                if timeoff.request_unit == 'day':
                                    extra_days = 0.83 * pre_month
                                    vals.update({
                                            'number_of_days': extra_days,
                                        })
                                elif timeoff.request_unit == 'hour':
                                    if employee.shift_id:
                                        tot_hours=(employee.shift_id.hours_per_day * (0.83 * pre_month))
                                    else:
                                        tot_hours=(8 * (0.83 * pre_month))
                                    vals.update({
                                            'number_of_hours_display': tot_hours,
                                        })
                                leave_obj = self.env['hr.leave.allocation'].create(vals)
                                if leave_obj:
                                    if next_execution_date < employee.confirm_date and (not fields.date.today().month==employee.confirm_date.month):
                                        leave_obj.update({
                                            'nextcall': next_execution_date
                                        })
                                    extra_days = 0.83 * pre_month
                                    leave_obj.update({
                                       'number_of_days': extra_days,
                                    })
                                    leave_obj.action_validate()
                                    employee.probation_leaves_allocated = True
                        else:
                            pass

    def schedular_confirmation(self):
        """
        Schedular For
        Time-Off: Pro-Rate Leave Allocation
        """
        current_date = date.today()
        employees_id = self.env['hr.employee'].search([])
         
        for employee in employees_id:
            time_off_for_probation = self.env['hr.leave.type'].search(
                [('allocated_during_probation', '=', True), ('fiscal_year', '=', current_date.year)
                    , ('company_id', '=', employee.company_id.id)])
            
            if employee.confirm_date and time_off_for_probation:
                if employee.confirm_date.year == current_date.year:
                    if employee.confirm_date < current_date:
                        num_of_days = 0
                        if employee.emp_type == 'permanent' or employee.emp_type == 'contractor':
                            if employee.pro_rate_leaves_allocated == False:
                                for timeoff in time_off_for_probation:
                                    if employee.emp_type == 'permanent':
                                        end_month = date(employee.confirm_date.year, 12, 31)
                                        delta = end_month - employee.confirm_date
                                        remaining = (delta.days / 365) * 12
                                        num_of_days = (12 / 12) * remaining

                                    elif employee.emp_type == 'contractor':
                                        end_month = date(employee.confirm_date.year, 12, 31)
                                        delta = end_month - employee.confirm_date
                                        remaining = (delta.days / 365) * 12
                                        num_of_days = (10 / 12) * remaining
                                    vals = {
                                        'name': 'Pro Rate Allocation For ' + employee.name,
                                        'holiday_status_id': timeoff.id,
                                        'allocation_type': 'regular',
                                        'holiday_type': 'employee',  # get from Selection
                                        'employee_id': employee.id,
                                        'number_of_days': num_of_days,
                                    }
                                    leave_obj = self.env['hr.leave.allocation'].create(vals)

                                    if leave_obj:
                                        leave_obj.action_validate()
                                        employee.pro_rate_leaves_allocated = True
                            else:
                                pass

    def schedular_pro_rate_annual_leaves(self):
        """
        Schedular For
        Time-Off: Pro-Rate Annual Leave Allocation
        """
        current_date = date.today()
        employees_id = self.env['hr.employee'].search([])
        current_date_year_ago = date.today() - relativedelta(days=365)
        for employee in employees_id:
            time_off_for_annual = self.env['hr.leave.type'].search(
                [('is_annual_leave', '=', True), ('fiscal_year', '=', current_date.year),
                 ('company_id', '=', employee.company_id.id)])
            if employee.date and time_off_for_annual:
                if employee.date == current_date_year_ago or employee.date < current_date_year_ago:
                    num_of_days = 0
                    if employee.emp_type == 'permanent':
                        if employee.pro_rate_annual_leaves_allocated == False:
                            for timeoff in time_off_for_annual:
                                if employee.emp_type == 'permanent':
                                    end_month = date(employee.confirm_date.year, 12, 31)
                                    delta = end_month - employee.confirm_date
                                    remaining = (delta.days / 365) * 21
                                    num_of_days = (12 / 12) * remaining
                                elif employee.emp_type == 'contractor':
                                    num_of_days = 0
                                vals = {
                                    'name': 'ProRate Annual Allocation For ' + employee.name,
                                    'holiday_status_id': timeoff.id,
                                    'allocation_type': 'regular',
                                    'holiday_type': 'employee',  # get from Selection
                                    'employee_id': employee.id,
                                    'number_of_days': num_of_days,
                                }
                                leave_obj = self.env['hr.leave.allocation'].create(vals)
                                if leave_obj:
                                    leave_obj.action_validate()
                                    employee.pro_rate_annual_leaves_allocated = True
                        else:
                            pass
