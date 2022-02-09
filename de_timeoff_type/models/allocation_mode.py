from odoo import fields, models, api, _


class AllocationModeEnhancement(models.Model):
    """
    """
    _inherit = 'hr.leave.allocation'

    holiday_type = fields.Selection([
        ('employee', 'By Employee'),
        ('company', 'By Company'),
        ('department', 'By Department'),
        ('category', 'By Employee Tag'),
        ('emp_type', 'By Employee Type')],
        string='Allocation Mode', readonly=True, required=True, default='employee',
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        help="Allow to create requests in batchs:\n- By Employee: for a specific employee"
             "\n- By Company: all employees of the specified company"
             "\n- By Department: all employees of the specified department"
             "\n- By Employee Tag: all employees of the specific employee group category"
             "\n- By Employee Typr: all employees of the specific employee Type")

    emp_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('contractor', 'Contractor'),
        ('freelancer', 'Freelancer'),
        ('inter', 'Intern'),
        ('part_time', 'Part Time'),
        ('project_based', 'Project Based Hiring'),
        ('outsource', 'Outsource'),
    ], string='Employee Type', track_visibility='onchange')

    _sql_constraints = [
        ('type_value',
         "CHECK( (holiday_type='employee' AND employee_id IS NOT NULL) or "
         "(holiday_type='category' AND category_id IS NOT NULL) or "
         "(holiday_type='department' AND department_id IS NOT NULL) or "
         "(holiday_type='company' AND mode_company_id IS NOT NULL)) or "
         "(holiday_type='emp_type' AND emp_type IS NOT NULL))",
         "The employee, department, company or employee category of this request is missing. Please make sure that your user login is linked to an employee."),
        ('duration_check', "CHECK ( number_of_days >= 0 )", "The number of days must be greater than 0."),
        ('number_per_interval_check', "CHECK(number_per_interval > 0)",
         "The number per interval should be greater than 0"),
        ('interval_number_check', "CHECK(interval_number > 0)", "The interval number should be greater than 0"),
    ]

    @api.depends('holiday_type')
    def _compute_from_holiday_type(self):
        for allocation in self:
            if allocation.holiday_type == 'employee':
                if not allocation.employee_id:
                    allocation.employee_id = self.env.user.employee_id
                allocation.mode_company_id = False
                allocation.category_id = False
            if allocation.holiday_type == 'company':
                allocation.employee_id = False
                if not allocation.mode_company_id:
                    allocation.mode_company_id = self.env.company
                allocation.category_id = False
            elif allocation.holiday_type == 'department':
                allocation.employee_id = False
                allocation.mode_company_id = False
                allocation.category_id = False
            elif allocation.holiday_type == 'category':
                allocation.employee_id = False
                allocation.mode_company_id = False
            elif allocation.holiday_type == 'emp_type':
                allocation.employee_id = False
                allocation.mode_company_id = False
                allocation.category_id = False
            elif not allocation.employee_id and not allocation._origin.employee_id:
                allocation.employee_id = self.env.context.get('default_employee_id') or self.env.user.employee_id

    @api.depends('holiday_type', 'employee_id')
    def _compute_department_id(self):
        for allocation in self:
            if allocation.holiday_type == 'employee':
                allocation.department_id = allocation.employee_id.department_id
            elif allocation.holiday_type == 'department':
                if not allocation.department_id:
                    allocation.department_id = self.env.user.employee_id.department_id
            elif allocation.holiday_type == 'category':
                allocation.department_id = False
            elif allocation.holiday_type == 'emp_type':
                allocation.department_id = False

    def _action_validate_create_childs(self):
        childs = self.env['hr.leave.allocation']
        if self.state == 'validate' and self.holiday_type in ['category', 'department', 'company', 'emp_type']:
            if self.holiday_type == 'category':
                employees = self.category_id.employee_ids
            elif self.holiday_type == 'department':
                employees = self.department_id.member_ids
            elif self.holiday_type == 'emp_type':
                employees = self.env['hr.employee'].search([('company_id', '=', self.holiday_status_id.company_id.id),('emp_type', '=', self.emp_type)])
            else:
                employees = self.env['hr.employee'].search([('company_id', '=', self.mode_company_id.id)])

            for employee in employees:
                childs += self.with_context(
                    mail_notify_force_send=False,
                    mail_activity_automation_skip=True
                ).create(self._prepare_holiday_values(employee))

            # TODO is it necessary to interleave the calls?
            childs.action_approve()
            if childs and self.validation_type == 'both':
                childs.action_validate()
        return childs
