# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime




class HrAttendanceRectification(models.Model):
    _name = 'hr.attendance.rectification'
    _description = 'Attendance Rectification'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    user_id = fields.Many2one('res.users', string="User")
    category_id = fields.Many2one(related='employee_id.category_id')
    check_in = fields.Datetime(string="Check In", required=True)
    check_out = fields.Datetime(string="Check Out", required=True)
    approval_request_id = fields.Many2one('approval.request', string="Approval")
    date = fields.Date(string="Date")
    reason =  fields.Text(string="Reason")
    attendance_id = fields.Many2one('hr.attendance', string="Attendance")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
         ],
        readonly=True, string='State', default='draft')
    
    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        for attendance in self:
            if attendance.check_in and attendance.check_out:
#                 employee_attendance = self.env['hr.attendance'].search([('employee_id','=',attendance.employee_id.id)])
#                 for hr_attendance in employee_attendance:
#                     if str(attendance.check_in) >= str(hr_attendance.check_in) and str(attendance.check_out) <= str(hr_attendance.check_out):
#                         raise exceptions.UserError(_('Attendance Exist between selected range.Please Select Other than this "Check In" ' + str(attendance.check_in) +' "Check Out" '+ str(str(attendance.check_out))))
                if attendance.check_out < attendance.check_in:
                    raise exceptions.UserError(_('"Check Out" time cannot be earlier than "Check In" time.'+ str(attendance.check_out) ))
                     
               
    
    def action_submit(self):
        for line in self:
            line.update({
                'state': 'submitted'
            })
            
    def action_approve(self):
        for line in self:
            if line.attendance_id:
                attendance_rectify = self.env['hr.attendance'].search([('id','=',line.attendance_id.id)])
                
                attendance_rectify.update({
                    'check_in': line.check_in,
                    'check_out': line.check_out,
                })
                line.update({
                    'state': 'approved'
                }) 
            else:
                vals = {
                    'employee_id': line.employee_id.id,
                    'check_in': line.check_in,
                    'check_out': line.check_out,
                }
                attendance = self.env['hr.attendance'].create(vals)
                line.update({
                    'state': 'approved'
                }) 
                
            
    def action_refuse(self):
        for line in self:
            line.update({
                'state': 'refused'
            })
            rectification_approval = self.env['approval.request'].search([('rectification_id','=', line.id)], limit=1)
            rectification_approval.action_cancel()
            
            
            
            
            
    @api.model
    def create(self, vals):
        sheet = super(HrAttendanceRectification, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)).create(vals)
        if sheet.category_id:
            sheet.action_create_approval_request_attendance()
        
        return sheet
    
    
    def action_create_approval_request_attendance(self):
        approver_ids  = []
        
        
        request_list = []
        for line in self:
            if line.category_id:
                request_list.append({
                        'name': line.employee_id.name + ' Has Attendance Rectification Request on ' + str(line.date)+ ' Check In ' + str(line.check_in)+' '+' Check Out '+str(line.check_out),
                        'request_owner_id': line.employee_id.user_id.id,
                        'category_id': line.category_id.id,
                        'rectification_id': line.id,
                        'reason': line.employee_id.name + ' Has Attendance Rectification Request on ' + str(line.date)+ ' Check In ' + str(line.check_in)+' '+' Check Out '+str(line.check_out),
                        'request_status': 'new',
                })
                approval_request_id = self.env['approval.request'].create(request_list)
                approval_request_id._onchange_category_id()
                approval_request_id.action_confirm()
                line.approval_request_id = approval_request_id.id


    
    

    