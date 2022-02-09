from datetime import date

from odoo import fields, models, api, _


class HrLeaveAllocationEnhance(models.Model):
    _inherit = 'hr.leave.allocation'

    target_year = fields.Selection([('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023')
                                       , ('2024', '2024'), ('2025', '2025'), ('2026', '2026'), ('2027', '2027')
                                       , ('2028', '2028'), ('2029', '2029'), ('2030', '2031'), ('2032', '2032')
                                       , ('2033', '2033'), ('2034', '2034'), ('2035', '2035'), ('2036', '2036')
                                       , ('2037', '2037'), ('2038', '2038'), ('2039', '2039'), ('2040', '2040')],
                                   string="Target Year", related='holiday_status_id.target_year')
    auto_allocation_boolean = fields.Boolean(string='Auto Allocation',
                                             default=False)  # to check For only run Auto Leave Allocation Functions

    def _action_validate_create_childs(self):

        childs = self.env['hr.leave.allocation']
        if self.state == 'validate' and self.holiday_type in ['category', 'department', 'company', 'emp_type']:
            if self.holiday_type == 'category':
                employees = self.category_id.employee_ids
            elif self.holiday_type == 'department':
                employees = self.department_id.member_ids
            elif self.holiday_type == 'emp_type':
                employees = self.env['hr.employee'].search(
                    [('company_id', '=', self.holiday_status_id.company_id.id)
                        , ('emp_type', '=', self.emp_type)])
            else:
                employees = self.env['hr.employee'].search([('company_id', '=', self.mode_company_id.id)])

            for employee in employees:
                if self.auto_allocation_boolean == True:
                    target = self.target_year
                    previous_year = int(target) - 1
                    previous_year_leave_type = self.env['hr.leave.type'].search(
                        [('target_year', '=', previous_year), ('code', '=', self.holiday_status_id.code)])
                    if previous_year_leave_type:
                        alloc_leaves = 0
                        consumed_leaves = 0
                        net_days = 0
                        for prev_type in previous_year_leave_type:

                            if prev_type.allow_carry_over == True:

                                get_allocated_leaves = self.env['hr.leave.report'].search(
                                    [('employee_id', '=', employee.id),
                                     ('holiday_status_id', '=', prev_type.id),
                                     ('state', '=', 'validate')])

                                for off_days in get_allocated_leaves:
                                    alloc_leaves = alloc_leaves + off_days.number_of_days

                                get_consumed_leaves = self.env['hr.leave'].search(
                                    [('employee_id', '=', employee.id),
                                     ('holiday_status_id', '=', prev_type.id),
                                     ('state', '=', 'validate')])

                                for consum_days in get_consumed_leaves:
                                    consumed_leaves = consumed_leaves + consum_days.number_of_days

                        remaining_days = alloc_leaves - consumed_leaves

                        net_days = remaining_days + self.number_of_days

                        if self.holiday_status_id.max_balance_after_carry_over <= net_days:
                            self.number_of_days = self.holiday_status_id.max_balance_after_carry_over

                    if employee.confirm_date:
                        delta = date.today() - employee.confirm_date
                        if date.today() < employee.confirm_date:
                            # check That this employee Confirmation Date before Selected Run Date
                            continue

                        if self.holiday_status_id.is_annual_leave == True:
                            if delta.days < 365:
                                # check That this employee able to obtain annual leave or not
                                continue

                childs += self.with_context(
                    mail_notify_force_send=False,
                    mail_activity_automation_skip=True).create(self._prepare_holiday_values(employee))
            # TODO is it necessary to interleave the calls?
            childs.action_approve()
            if childs and self.validation_type == 'both':
                childs.action_validate()
        return childs
