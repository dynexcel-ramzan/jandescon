# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
    

class HrAttendanceWFH(models.Model):
    _name = 'hr.attendance.wfh'
    _description = 'Work From Home'
    
    def _default_employee(self):
        return self.env.user.employee_id

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, ondelete='cascade', index=True)
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
        readonly=True)
    date = fields.Date(string='Date')
    check_in = fields.Datetime(string="Check In")
    check_out = fields.Datetime(string="Check Out")
    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)
    
    category_id = fields.Many2one('approval.category', string="Category", required=False)
    approval_request_id = fields.Many2one('approval.request', string='Approval Request', copy=False, readonly=True)
    company_id = fields.Many2one('res.company', string="Company", required=False)
    reason= fields.Char(string='Reason')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
         ],
        readonly=True, string='State', default='draft')
   
    @api.constrains('employee_id')
    def _check_employee_id(self):  
        for line in self:
            if line.employee_id:
                line.update({
                    'company_id': line.employee_id.company_id.id, 
                })

    def action_submit(self):
        approver_ids  = []
        request_list = []
        for line in self:
            if line.check_in and line.check_out:
                check_in=line.check_in + relativedelta(hours =+ 5) 
                check_out=line.check_out + relativedelta(hours =+ 5) 
                expense_category=self.env['approval.category'].search([('name','=','WFH(Work From Home)'),('company_id','=', line.company_id.id)], limit=1)
                if not expense_category:
                    category = {
                        'name': 'WFH(Work From Home)',
                        'company_id': line.employee_id.company_id.id,
                        'is_parent_approver': True,
                    }
                    expense_category = self.env['approval.category'].sudo().create(category)
                line.category_id=expense_category.id
                request_list.append({
                    'name': 'Work From Home Attendance',
                    'request_owner_id': line.employee_id.user_id.id,
                    'category_id': line.category_id.id,
                    'wfh_id': line.id,
                    'reason': line.employee_id.name + ' Work from home attendance ' + str(line.date.strftime('%d/%b/%y'))+ ' Check In: ' + str(check_in.strftime('%d/%b/%y %H:%M:%S'))+ ' Check Out:  ' +' ' + str(check_out.strftime('%d/%b/%y %H:%M:%S')), 
                    'request_status': 'new',
                })
                approval_request_id = self.env['approval.request'].create(request_list)        
                approval_request_id._onchange_category_id()
                approval_request_id.action_confirm()
                line.approval_request_id = approval_request_id.id
                line.update({
                    'state': 'submitted',
                })

    def action_approve(self):
        for line in self:
            existing_attendance=self.env['hr.attendance'].sudo().search([('employee_id','=', line.employee_id.id),('check_in','>=',line.check_in),('check_out','<=',line.check_out)], limit=1)
            existing_inattendance=self.env['hr.attendance'].sudo().search([('employee_id','=', line.employee_id.id),('check_in','>=',line.check_in),('check_in','<=',line.check_out)], limit=1)
            existing_outattendance=self.env['hr.attendance'].sudo().search([('employee_id','=', line.employee_id.id),('check_out','>=',line.check_in),('check_out','<=',line.check_out)], limit=1)
            if not existing_attendance and not existing_inattendance and not existing_outattendance:
                att_vals = {
                    'employee_id': line.employee_id.id,
                    'check_in': line.check_in,
                    'check_out': line.check_out,
                    'att_date': line.date,
                    'remarks': 'WFH(Work From Home)',
                }
                attendance=self.env['hr.attendance'].sudo().create(att_vals)
                line.update({
                    'state': 'approved'
                })
            
    def action_refuse(self):
        for line in self:
            line.update({
                'state': 'refused'
            })
            
    def unlink(self):
        for wfh in self:
            if wfh.state not in ('draft','refused'):
                raise UserError(_('You cannot delete an Document  which is not draft or cancelled. '))
     
            return super(HrAttendanceWFH, self).unlink()          
    
    def name_get(self):
        result = []
        for attendance in self:
            if not attendance.check_out:
                result.append((attendance.id, _("%(empl_name)s from %(check_in)s") % {
                    'empl_name': attendance.employee_id.name,
                    'check_in': format_datetime(self.env, attendance.check_in, dt_format=False),
                }))
            else:
                result.append((attendance.id, _("%(empl_name)s from %(check_in)s to %(check_out)s") % {
                    'empl_name': attendance.employee_id.name,
                    'check_in': format_datetime(self.env, attendance.check_in, dt_format=False),
                    'check_out': format_datetime(self.env, attendance.check_out, dt_format=False),
                }))
        return result

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = False

    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                if attendance.check_out < attendance.check_in:
                    raise exceptions.ValidationError(_('"Check Out" time cannot be earlier than "Check In" time.'))

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
                pass

            if not attendance.check_out:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if no_check_out_attendances:
                    pass
            else:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_in', '<', attendance.check_out),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
                    pass

    @api.returns('self', lambda value: value.id)
    def copy(self):
        raise exceptions.UserError(_('You cannot duplicate an attendance.'))
    


    
    