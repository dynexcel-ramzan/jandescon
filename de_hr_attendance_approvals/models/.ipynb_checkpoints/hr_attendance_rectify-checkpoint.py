# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError



class HrAttendanceRectification(models.Model):
    _name = 'hr.attendance.rectification'
    _description = 'Attendance Rectification'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    user_id = fields.Many2one('res.users', string="User")
    category_id = fields.Many2one(related='employee_id.category_id')
    app_date = fields.Date(string='Approve Date')
    check_in = fields.Datetime(string="Check In", required=True)
    check_out = fields.Datetime(string="Check Out", required=True)
    approval_request_id = fields.Many2one('approval.request', string="Approval")
    date = fields.Date(string="Date")
    reason =  fields.Text(string="Reason")
    partial = fields.Selection(selection=[
            ('Full', 'Full'),
            ('Partial', 'Partial'),
            ('Check In Time Missing', 'Check In Time Missing'),
            ('Out Time Missing', 'Out Time Missing'),
        ], string='Type', required=True,
        )
    attendance_id = fields.Many2one('hr.attendance', string="Attendance")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
         ],
        readonly=True, string='State', default='draft')
    number_of_Days = fields.Integer(string='Number Of Days', compute='_compute_number_of_days')
    
    
    @api.constrains('check_in', 'check_out')
    def _compute_number_of_days(self):
        for line in self:
            if line.check_out and line.check_in:
                delta_diff = line.check_out - line.check_in
                delta_days = delta_diff.days
                line.update({
                    'number_of_Days': delta_days
                })    
            else:
                line.update({
                    'number_of_Days': 0
                })
    
    @api.constrains('check_in', 'check_out')
    def _check_attendance_date(self):
        for line in self:
            if line.check_in:
                line.update({
                    'date': line.check_in + relativedelta(hours =+ 5) 
                })
            elif line.check_out:
                line.update({
                    'date': line.check_out + relativedelta(hours =+ 5)
                })    
    
    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                hr_attendance = self.env['hr.attendance'].search([('employee_id','=',attendance.employee_id.id),('att_date','=',attendance.date)])
                for line in hr_attendance:
                    if line.check_in and line.check_out:
                        if str(attendance.check_in) >= str(line.check_in) and str(attendance.check_in) <= str(line.check_out):
                            raise exceptions.UserError(_('Attendance Already Exist between selected range!'))
                                    
                if attendance.check_out < attendance.check_in:
                    raise exceptions.UserError(_('"Check Out" time cannot be earlier than "Check In" time.'+ str(attendance.check_out) ))
                    
            if attendance.date:
#                 attendance_present = self.env['hr.attendance'].search([('employee_id','=',attendance.employee_id.id),('att_date','=',attendance.date),('check_in','>=', attendance.check_in),('check_out','<=', attendance.check_out)])
#                 if attendance_present:
#                     raise exceptions.UserError(_('Attendance Already Exist between selected range!'+ str(attendance.check_in + relativedelta(hours =+ 5))+' to '+str(attendance.check_out+ relativedelta(hours =+ 5))))         
                rectification = self.env['hr.attendance.rectification'].search([('employee_id','=',attendance.employee_id.id),('date','=',attendance.date),('state','in',('submitted','approved'))])
                if rectification:
                    raise exceptions.UserError(_('Attendance Rectification Already Exist between selected range!'))         
               
    
    def action_submit(self):
        for line in self:
            line.update({
                'state': 'submitted'
            })
            
    def action_approve(self):
        for line in self:
            if line.state =='submitted':
                line.app_date = fields.date.today()
                if line.attendance_id:
                    count = 0
                    attendance_rectify = self.env['hr.attendance'].search([('id','=',line.attendance_id.id)])  
                    attendance_rectify.update({
                      'check_in': line.check_in,
                      'att_date':  line.check_in,
                      'check_out': line.check_out,
                      'remarks':line.partial,
                    })
                    line.update({
                      'state': 'approved'
                    })
                elif  line.partial == 'Partial':
                    vals = {
                            'employee_id': line.employee_id.id,
                            'check_in': line.check_in,
                            'att_date':  line.check_out,
                            'check_out': line.check_out,
                            'remarks': 'Partial',
                        }
                    attendance = self.env['hr.attendance'].sudo().create(vals)
                    line.update({
                            'state': 'approved'
                    }) 
                else:
                    if line.number_of_Days == 0:
                        vals = {
                            'employee_id': line.employee_id.id,
                            'check_in': line.check_in,
                            'att_date':  line.check_out,
                            'check_out': line.check_out,
                            'remarks': 'Comitment Slip',
                        }
                        attendance = self.env['hr.attendance'].sudo().create(vals)
                        line.update({
                            'state': 'approved'
                        }) 
                    else:
                        if line.check_in and line.check_out:
                            delta_days_count = line.number_of_Days + 1
                            for day in range(delta_days_count):
                                check_ina = line.check_in.strftime("%y-%m-%d")
                                check_inaa = datetime.strptime(str(check_ina),'%y-%m-%d')
                                check_in = check_inaa + timedelta(day)
                                hour_from = 4
                                hour_to = 8

                                shift_time = self.env['resource.calendar'].search([('company_id','=',line.employee_id.company_id.id),('shift_type','=','general')], limit=1)
                                if line.employee_id.shift_id:
                                    shift_time =  line.employee_id.shift_id   
                                shift_line = self.env['hr.shift.schedule.line'].search([('employee_id','=',line.employee_id.id),('date','=',check_in)], limit=1)

                                if shift_line.first_shift_id:
                                    shift_time = shift_line.first_shift_id

                                for  shift_line in shift_time.attendance_ids:
                                    hour_from = shift_line.hour_from
                                    hour_to = shift_line.hour_to
                                final_check_in= check_in + relativedelta(hours =+ hour_from)
                                check_out = check_in + relativedelta(hours =+ hour_to)
                                if shift_time.shift_type == 'night':
                                    check_out = check_out +  timedelta(1) 
                                vals = {
                                    'employee_id': line.employee_id.id,
                                    'check_in':final_check_in - relativedelta(hours =+ 5),
                                    'att_date':  final_check_in,
                                    'check_out': check_out - relativedelta(hours =+ 5),
                                    'remarks': 'Comitment Slip',
                                    }
                                attendance = self.env['hr.attendance'].sudo().create(vals)
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
        sheet.action_validate_comitment_period()
        return sheet
    
    def action_validate_comitment_period(self):
        restrict_date = '2021-07-16'
        for line in self:
            if str(line.date)  < restrict_date:
                raise UserError('Not Allow to Enter Rectification Request before 16 JULY 2021!') 
    
    def action_create_approval_request_attendance(self):
        approver_ids  = []
        
        
        request_list = []
        for line in self:
            check_in = False
            check_out = False
            if line.check_in:
                check_in = line.check_in + relativedelta(hours =+ 5)
            if line.check_out:
                check_out = line.check_out + relativedelta(hours =+ 5)
            if line.category_id:
                request_list.append({
                        'name':  str(line.employee_id.name ),
                        'request_owner_id': line.employee_id.user_id.id,
                        'category_id': line.category_id.id,
                        'rectification_id': line.id,
                        'reason': ' Check In: ' + str(check_in)+"\n"+' Check Out: '+str(check_out)+"\n" +"\n" +"\n" + ' Remarks:   ' +str(line.reason)+"\n",
                        'request_status': 'new',
                })
                approval_request_id = self.env['approval.request'].create(request_list)
                approval_request_id._onchange_category_id()
                approval_request_id.action_confirm()
                approval_request_id.action_date_confirm_update()
                line.approval_request_id = approval_request_id.id


    
    

    