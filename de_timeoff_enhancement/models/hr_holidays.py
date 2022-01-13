# -*- coding: utf-8 -*-
from odoo import api, fields, models
from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError


def split_string_into_integer(a_string):
    """
    Function to extract numeric from string and
    it will return list of numbers
    """
    numbers = []
    for word in a_string:
        if word.isdigit():
            numbers.append(int(word))
    return numbers


class AutomaticLeaveAllocation(models.Model):
    _name = "automatic.leave.allocation"
    _description = "Automatic Leave Allocation"
    _inherit = ['mail.thread']

    name = fields.Char('Description')
    active = fields.Boolean('Active', default=True)
    # leave_type_id = fields.Many2one("hr.leave.type",
    #                                 string="Leave Type", copy=False,
    #                                 track_visibility='onchange')
    # type_request_unit = fields.Selection(
    #     related='leave_type_id.request_unit', readonly=True)
    type = fields.Selection(
        [('prorata', 'Pro-Rata'), ('full', 'Full')], string='Type', copy=False, default='full')
    no_of_days = fields.Float('No of Days')
    no_of_hours = fields.Float('No of Hours')
    alloc_by = fields.Selection([('by_emp', 'By Employee'),
                                 # ('by_company', 'By Company'),
                                 # ('by_dept', 'By Department'),
                                 # ('by_tag', 'By Employee Tag'),
                                 ('by_type', 'By Employee Type')],
                                default='by_emp',
                                string='Allocation By')  # Update
    target_year = fields.Selection([('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023')
                                       , ('2024', '2024'), ('2025', '2025'), ('2026', '2026'), ('2027', '2027')
                                       , ('2028', '2028'), ('2029', '2029'), ('2030', '2031'), ('2032', '2032')
                                       , ('2033', '2033'), ('2034', '2034'), ('2035', '2035'), ('2036', '2036')
                                       , ('2037', '2037'), ('2038', '2038'), ('2039', '2039'), ('2040', '2040')],
                                   string='Target Year')

    run_date = fields.Date('Run Date')  # Update
    emp_ids = fields.Many2many('hr.employee',
                               string='Employees', )
    # company_id = fields.Many2one(
    #     'res.company',
    #     default=lambda self: self.env.user.company_id.id,
    #     track_visibility='onchange')
    # dept_ids = fields.Many2many('hr.department',
    #                             string='Departments',
    #                             track_visibility='onchange')
    # tag_ids = fields.Many2many('hr.employee.category',
    #                            string='Tags',
    #                            track_visibility='onchange')
    timeoff_types = fields.Many2many('hr.leave.type',
                                     string="Time Off Type")
    employee_timeoff_ids = fields.One2many('employee.timeoff.type', 'allocation_id')  # link Line Model Here

    @api.onchange('target_year')
    def _onchange_target_year(self):
        ids = []
        if self.target_year:
            type_id = self.env['hr.leave.type'].search([('target_year', '=', self.target_year)])
            for rec in type_id:
                ids.append(rec.id)
            return {'domain': {'timeoff_types': [('id', '=', ids)]}}

    @api.constrains('run_date')
    def run_date_restriction(self):
        if self.run_date < fields.Date.today():
            raise UserError("Run Date Should be at least 1 Day After")

    @api.onchange('timeoff_type', 'alloc_by')
    def time_type(self):
        for link in self.employee_timeoff_ids:
            link.unlink()
        # self.employee_timeoff_ids.unlink()
        # if self.alloc_by == 'by_type':
        for type in self.timeoff_types.ids:
            self.env['employee.timeoff.type'].create({
                'timeoff_type_id': type,
                'allocation_id': self.id,
            })

    def allocate_leaves(self):

        leave_alloc_obj = self.env['hr.leave.allocation']
        """
        al contain automatic_leave_alloc_obj=self 
        """
        for al in self:
            if al.employee_timeoff_ids:
                for record in al.employee_timeoff_ids:
                    if record.permanent > 0:
                        leave_obj = leave_alloc_obj.create({
                            'name': 'Auto-Leave Allocation for ' + al.name + ' with Emp Type Permanent',
                            'holiday_status_id': record.timeoff_type_id.id,
                            'allocation_type': 'regular',
                            'holiday_type': 'emp_type',  # get from Selection
                            'emp_type': 'permanent',
                            'number_of_days_display': record.permanent,
                            'number_of_days': record.permanent,
                            'auto_allocation_boolean': True,
                            'interval_number': 1,
                            'number_per_interval': 1,
                            'employee_id': False,
                            'number_of_hours_display': False,

                        })
                        if record.timeoff_type_id.leave_validation_type == 'both':
                            leave_obj.action_approve()
                            if leave_obj.state == 'validate':
                                pass
                            else:
                                leave_obj.action_validate()
                        else:
                            leave_obj.action_approve()

                    if record.contractor > 0:
                        leave_obj = leave_alloc_obj.create({
                            'name': 'Auto-Leave Allocation for ' + al.name + ' with Emp Type Contractor',
                            'holiday_status_id': record.timeoff_type_id.id,
                            'allocation_type': 'regular',
                            'holiday_type': 'emp_type',  # get from Selection
                            'emp_type': 'contractor',
                            'number_of_days_display': record.contractor,
                            'number_of_days': record.contractor,
                            'auto_allocation_boolean': True,
                            'interval_number': 1,
                            'number_per_interval': 1,
                            'employee_id': False,
                            'number_of_hours_display': False,

                        })
                        if record.timeoff_type_id.leave_validation_type == 'both':
                            leave_obj.action_approve()
                            if leave_obj.state == 'validate':
                                pass
                            else:
                                leave_obj.action_validate()
                        else:
                            leave_obj.action_approve()

                    if record.freelancer > 0:
                        leave_obj = leave_alloc_obj.create({
                            'name': 'Auto-Leave Allocation for ' + al.name + 'with Emp Type Freelancer',
                            'holiday_status_id': record.timeoff_type_id.id,
                            'allocation_type': 'regular',
                            'holiday_type': 'emp_type',  # get from Selection
                            'emp_type': 'freelancer',
                            'number_of_days_display': record.freelancer,
                            'number_of_days': record.freelancer,
                            'auto_allocation_boolean': True,
                            'interval_number': 1,
                            'number_per_interval': 1,
                            'employee_id': False,
                            'number_of_hours_display': False,

                        })

                        if record.timeoff_type_id.leave_validation_type == 'both':
                            leave_obj.action_approve()

                            if leave_obj.state == 'validate':
                                pass
                            else:
                                leave_obj.action_validate()
                        else:
                            leave_obj.action_approve()

                    if record.intern > 0:
                        leave_obj = leave_alloc_obj.create({
                            'name': 'Auto-Leave Allocation for ' + al.name + 'with Emp Type Intern',
                            'holiday_status_id': record.timeoff_type_id.id,
                            'allocation_type': 'regular',
                            'holiday_type': 'emp_type',  # get from Selection
                            'emp_type': 'inter',
                            'number_of_days_display': record.intern,
                            'number_of_days': record.intern,
                            'auto_allocation_boolean': True,
                            'interval_number': 1,
                            'number_per_interval': 1,
                            'employee_id': False,
                            'number_of_hours_display': False,

                        })
                        if record.timeoff_type_id.leave_validation_type == 'both':
                            leave_obj.action_approve()
                            if leave_obj.state == 'validate':
                                pass
                            else:
                                leave_obj.action_validate()
                        else:
                            leave_obj.action_approve()

                    if record.part_time > 0:
                        leave_obj = leave_alloc_obj.create({
                            'name': 'Auto-Leave Allocation for ' + al.name + 'with Emp Type Part Time',
                            'holiday_status_id': record.timeoff_type_id.id,
                            'allocation_type': 'regular',
                            'holiday_type': 'emp_type',  # get from Selection
                            'emp_type': 'part_time',
                            'number_of_days_display': record.part_time,
                            'number_of_days': record.part_time,
                            'auto_allocation_boolean': True,
                            'interval_number': 1,
                            'number_per_interval': 1,
                            'employee_id': False,
                            'number_of_hours_display': False,

                        })

                        if record.timeoff_type_id.leave_validation_type == 'both':
                            leave_obj.action_approve()
                            if leave_obj.state == 'validate':
                                pass
                            else:
                                leave_obj.action_validate()
                        else:
                            leave_obj.action_approve()

                    if record.project_based > 0:
                        leave_obj = leave_alloc_obj.create({
                            'name': 'Auto-Leave Allocation for ' + al.name + 'with Emp Type Project Based',
                            'holiday_status_id': record.timeoff_type_id.id,
                            'allocation_type': 'regular',
                            'holiday_type': 'emp_type',  # get from Selection
                            'emp_type': 'project_based',
                            'number_of_days_display': record.project_based,
                            'number_of_days': record.project_based,
                            'auto_allocation_boolean': True,
                            'interval_number': 1,
                            'number_per_interval': 1,
                            'employee_id': False,
                            'number_of_hours_display': False,

                        })
                        if record.timeoff_type_id.leave_validation_type == 'both':
                            leave_obj.action_approve()
                            if leave_obj.state == 'validate':
                                pass
                            else:
                                leave_obj.action_validate()
                        else:
                            leave_obj.action_approve()

                    if record.outsource > 0:
                        leave_obj = leave_alloc_obj.create({
                            'name': 'Auto-Leave Allocation for' + al.name + 'with Emp Type Out Source',
                            'holiday_status_id': record.timeoff_type_id.id,
                            'allocation_type': 'regular',
                            'holiday_type': 'emp_type',  # get from Selection
                            'emp_type': 'outsource',
                            'number_of_days_display': record.outsource,
                            'number_of_days': record.outsource,
                            'auto_allocation_boolean': True,
                            'interval_number': 1,
                            'number_per_interval': 1,
                            'employee_id': False,
                            'number_of_hours_display': False,
                        })
                        if record.timeoff_type_id.leave_validation_type == 'both':
                            leave_obj.action_approve()
                            if leave_obj.state == 'validate':
                                # print("Continue Statement Run Good Bye!")
                                pass
                            else:
                                leave_obj.action_validate()
                        else:
                            leave_obj.action_approve()

    @api.model
    def _auto_alloc_leaves(self):
        """
        This is a scheduler method that will check the dates and allocate the leaves
        ----------------------------------------------------------------------------
        @param self: object pointer
        """
        print("Schedular Run")
        # Search for allocation configurations
        allocs = self.search(['|', ('run_date', '=', fields.Date.today())])
        # Allocate Leaves
        allocs.allocate_leaves()


class AutomaticLeaveAllocationEmployeeType(models.Model):
    _name = 'employee.timeoff.type'
    _description = 'Employees with Time Off and Days'

    timeoff_type_id = fields.Many2one('hr.leave.type', string="Leave Type")
    allocation_id = fields.Many2one('automatic.leave.allocation', string="Automatic Allocation ID")
    permanent = fields.Integer('Permanent')
    contractor = fields.Integer('Contractor')
    freelancer = fields.Integer('Freelancer')
    intern = fields.Integer('Intern')
    part_time = fields.Integer('Part Time')
    project_based = fields.Integer('Project Based')
    outsource = fields.Integer('OutSource')
