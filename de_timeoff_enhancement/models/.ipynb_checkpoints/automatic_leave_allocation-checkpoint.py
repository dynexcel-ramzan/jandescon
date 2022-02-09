# -*- coding: utf-8 -*-
from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta

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
    company_id = fields.Many2one('res.company' , string='Company', required=True)
    no_of_days = fields.Float('No of Days')
    no_of_hours = fields.Float('No of Hours')
    alloc_by = fields.Selection([('by_type', 'By Employee Type')],
                                default='by_type',
                                string='Allocation By')  # Update
    fiscal_year_id = fields.Many2one('fiscal.year' , string='Target Year', required=True)
    fiscal_start_date = fields.Date('Fiscal Year Start Date', required=True)  # Update
    run_date = fields.Date('Run Date', required=True)  # Update
    leave_allocated = fields.Boolean(string='Leave Allocation') 
    employee_timeoff_ids = fields.One2many('employee.timeoff.type', 'allocation_id')  # link Line Model Here
    
    
    def unlink(self):
        for leave in self:
            if leave.leave_allocated==True:
                raise UserError(_('You cannot delete an Reconciled Document!'))
            return super(AutomaticLeaveAllocation, self).unlink()  
    
    @api.constrains('run_date')
    def run_date_restriction(self):
        if self.run_date < fields.Date.today():
            raise UserError("Run Date Should be at least 1 Day After")

    def allocate_leaves(self):
        leave_alloc_obj = self.env['hr.leave.allocation']
        """
        al contain automatic_leave_alloc_obj=self 
        """
        for al in self:
            fiscal_start_date = al.fiscal_start_date - timedelta(365)
            if al.leave_allocated==False:
                if al.employee_timeoff_ids:
                    for record in al.employee_timeoff_ids:
                        if record.permanent > 0:
                            permanent_employees=self.env['hr.employee'].search([('emp_type','=','permanent'),('company_id','=', al.company_id.id),('date','<=', fiscal_start_date)])
                            for permanent_employee in permanent_employees:
                                leave_obj = leave_alloc_obj.create({
                                    'name': 'Auto-Leave Allocation for ' + al.name + ' with Emp Type Permanent',
                                    'holiday_status_id':  record.timeoff_type_id.id,
                                    'employee_id': permanent_employee.id,
                                    'state': 'confirm',
                                    'number_of_days_display': record.permanent,
                                    'number_of_days': record.permanent,
                                })
                                leave_obj.update({
                                    'number_of_days_display': record.permanent,
                                    'number_of_days': record.permanent,
                                })
                                leave_obj.action_approve()
                                if leave_obj.state == 'validate':
                                    pass
                                else:
                                    leave_obj.action_validate()
                                
                        if record.contractor > 0:
                            contractor_employees=self.env['hr.employee'].search([('emp_type','=','contractor'),('company_id','=', al.company_id.id),('date','<=', fiscal_start_date)])
                            for contractor_employee in contractor_employees:
                                leave_obj = leave_alloc_obj.create({
                                    'name': 'Auto-Leave Allocation for ' + al.name + ' with Emp Type Contractor',
                                    'holiday_status_id':  record.timeoff_type_id.id,
                                    'state': 'confirm',
                                    'employee_id': contractor_employee.id,
                                    'number_of_days_display': record.contractor,
                                    'number_of_days': record.contractor,
                                })
                                leave_obj.update({
                                    'number_of_days_display': record.contractor,
                                    'number_of_days': record.contractor,
                                })
                                leave_obj.action_approve()
                                if leave_obj.state == 'validate':
                                    pass
                                else:
                                    leave_obj.action_validate()
                                        
                        if record.freelancer > 0:
                            freelancer_employees=self.env['hr.employee'].search([('emp_type','=','freelancer'),('company_id','=', al.company_id.id),('date','<=', fiscal_start_date)])
                            for freelancer_employee in freelancer_employees:
                                leave_obj = leave_alloc_obj.create({
                                    'name': 'Auto-Leave Allocation for ' + al.name + 'with Emp Type Freelancer',
                                    'holiday_status_id':  record.timeoff_type_id.id,
                                    'employee_id': freelancer_employee.id,
                                    'state': 'confirm',
                                    'number_of_days_display': record.freelancer,
                                    'number_of_days': record.freelancer,
                                })
                                leave_obj.update({
                                    'number_of_days_display': record.freelancer,
                                    'number_of_days': record.freelancer,
                                })
                                leave_obj.action_approve()
                                if leave_obj.state == 'validate':
                                    pass
                                else:
                                    leave_obj.action_validate()
                        if record.intern > 0:
                            intern_employees=self.env['hr.employee'].search([('emp_type','=','intern'),('company_id','=', al.company_id.id),('date','<=', fiscal_start_date)])
                            for intern_employee in intern_employees:
                                leave_obj = leave_alloc_obj.create({
                                    'name': 'Auto-Leave Allocation for ' + al.name + 'with Emp Type Intern',
                                    'holiday_status_id':  record.timeoff_type_id.id,
                                    'employee_id': intern_employee.id,
                                    'state': 'confirm',
                                    'number_of_days_display': record.intern,
                                    'number_of_days': record.intern,
                                })
                                leave_obj.update({
                                    'number_of_days_display': record.intern,
                                    'number_of_days': record.intern,
                                })
                                leave_obj.action_approve()
                                if leave_obj.state == 'validate':
                                    pass
                                else:
                                    leave_obj.action_validate()
                        if record.part_time > 0:
                            part_time_employees=self.env['hr.employee'].search([('emp_type','=','part_time'),('company_id','=', al.company_id.id),('date','<=', fiscal_start_date)])
                            for part_time_employee in part_time_employees:
                                leave_obj = leave_alloc_obj.create({
                                    'name': 'Auto-Leave Allocation for ' + al.name + 'with Emp Type Part Time',
                                    'holiday_status_id':  record.timeoff_type_id.id,
                                    'employee_id': part_time_employee.id,
                                    'state': 'confirm',
                                    'number_of_days_display': record.part_time,
                                    'number_of_days': record.part_time,
                                })
                                leave_obj.update({
                                    'number_of_days_display': record.part_time,
                                    'number_of_days': record.part_time,
                                })
                                leave_obj.action_approve()
                                if leave_obj.state == 'validate':
                                    pass
                                else:
                                    leave_obj.action_validate()
                        if record.project_based > 0:
                            project_based_employees=self.env['hr.employee'].search([
                            ('emp_type','=','project_based'),('company_id','=', al.company_id.id),
                            ('date','<=', fiscal_start_date)])
                            for project_based_employee in project_based_employees:
                                leave_obj = leave_alloc_obj.create({
                                    'name': 'Auto-Leave Allocation for ' + al.name + 'with Emp Type Project Based',
                                    'holiday_status_id':  record.timeoff_type_id.id,
                                    'state': 'confirm',
                                    'employee_id': project_based_employee.id,
                                    'number_of_days_display': record.project_based,
                                    'number_of_days': record.project_based,
                                })
                                leave_obj.update({
                                    'number_of_days_display': record.project_based,
                                    'number_of_days': record.project_based,
                                })
                                leave_obj.action_approve()
                                if leave_obj.state == 'validate':
                                    pass
                                else:
                                    leave_obj.action_validate()
                        if record.outsource > 0:
                            outsource_employees=self.env['hr.employee'].search([('emp_type','=','outsource'),('company_id','=', al.company_id.id),('date','<=', fiscal_start_date)])
                            for outsource_employee in outsource_employees:
                                leave_obj = leave_alloc_obj.create({
                                    'name': 'Auto-Leave Allocation for' + al.name + 'with Emp Type Out Source',
                                    'holiday_status_id':  record.timeoff_type_id.id,
                                    'employee_id': outsource_employee.id,
                                    'state': 'confirm',
                                    'number_of_days_display': record.outsource,
                                    'number_of_days': record.outsource,
                                })
                                leave_obj.update({
                                    'number_of_days_display': record.outsource,
                                    'number_of_days': record.outsource,
                                })
                                leave_obj.action_approve()
                                if leave_obj.state == 'validate':
                                    pass
                                else:
                                    leave_obj.action_validate()
                al.update({
                  'leave_allocated': True
                })
            
       
    
    @api.model
    def _auto_alloc_leaves(self):
        """
        This is a scheduler method that will check the dates and allocate the leaves
        ----------------------------------------------------------------------------
        @param self: object pointer
        """
        print("Schedular Run")
        # Search for allocation configurations
        allocations = self.env['automatic.leave.allocation'].search([('run_date', '=', fields.Date.today()),('leave_allocated','=',False)])
        # Allocate Leaves
        for auto_allocate in allocations:
            auto_allocate.allocate_leaves()


class AutomaticLeaveAllocationEmployeeType(models.Model):
    _name = 'employee.timeoff.type'
    _description = 'Employees with Time Off and Days'

    timeoff_type_id = fields.Many2one('hr.leave.type', string="Leave Type", required=True)
    allocation_id = fields.Many2one('automatic.leave.allocation', string="Automatic Allocation ID")
    company_id = fields.Many2one('res.company' , string='Company')
    permanent = fields.Integer('Permanent')
    contractor = fields.Integer('Contractor')
    freelancer = fields.Integer('Freelancer')
    intern = fields.Integer('Intern')
    part_time = fields.Integer('Part Time')
    project_based = fields.Integer('Project Based')
    outsource = fields.Integer('OutSource')
