import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)



class OvertimesubmitWizard(models.TransientModel):
    _name = 'overtime.submit.wizard'
    _description = 'Overtime Timeoff Wizard'

   

    overtime_type_id = fields.Many2one('hr.overtime.type', string="Overtime Type", required=True)
    overtime_request_ids = fields.Many2many('hr.overtime.request', string="Overtime")
    
    def action_overtime_submit(self):
        for ovt in self.overtime_request_ids:
            if ovt.state == 'draft':
                ovt.update({
                    'overtime_type_id': self.overtime_type_id.id,
                    'state': 'to_approve',
                })
    



class OvertimeTimeoffWizard(models.TransientModel):
    _name = 'overtime.timeoff.wizard'
    _description = 'Overtime Timeoff Wizard'

   

    
    timeoff_id = fields.Many2many('hr.overtime.request', string="TimeOff")
    
    def action_create_timeoff(self):
        employee_ids = []
        leave_type_ids = []
        for ovt_emp in self.timeoff_id:
            employee_ids.append(ovt_emp.employee_id.id)
            leave_type_ids.append(ovt_emp.overtime_type_id.leave_type_id.id)
        uniq_employee = set(employee_ids) 
        uniq_leave_type = set(leave_type_ids) 
        for employeet in uniq_employee:
            employee = self.env['hr.employee'].search([('id','=',employeet)], limit=1)
            for leave_type in uniq_leave_type:
                default_leave_type = self.env['hr.leave.type'].search([('id','=', leave_type)], limit=1)
                leave_type_overtime = self.timeoff_id.search([('employee_id','=',employee.id),('overtime_type_id.leave_type_id','=',default_leave_type.id)])
#                 raise UserError(_(str(uniq_employee)+' '+str(uniq_leave_type)+ ' '+ str(employeet) +' '+str(default_leave_type.id)))
                if default_leave_type.request_unit == 'hour' or default_leave_type.request_unit == 'half_day':
                    total_hours = 0
                    for ovt in leave_type_overtime:
                        total_hours = total_hours + ovt.overtime_hours
                    if total_hours > 0: 
                        vals = {
                           'holiday_status_id': default_leave_type.id,
                            'employee_id': employee.id,            
                            'holiday_type': 'employee',
                            'allocation_type': 'regular',
                            'number_of_hours_display': total_hours,
                            'name':  "This Timeoff Request Created From Employee Overtime Compansation", 

                        }
                        timeoff = self.env['hr.leave.allocation'].create(vals)
                    for ovt in leave_type_overtime: 
                        ovt.update({
                                'state': 'approved'
                            })


                elif default_leave_type.request_unit == 'day':
                    total_hours = 0
                    day = 0 
                    for ovt in leave_type_overtime:
                        total_hours = total_hours + ovt.overtime_hours
                    days = total_hours / employee.resource_calendar_ids.hours_per_day
                    if days > 0: 
                        vals = {
                           'holiday_status_id': default_leave_type.leave_type_id.id,
                            'employee_id': employee.id,            
                            'holiday_type': 'employee',
                            'allocation_type': 'regular',
                            'number_of_days_display': days,
                            'request_date_to': self.date_to,
                            'name':  "This Timeoff Request Created From Employee Overtime Compansation", 

                        }
                        timeoff = self.env['hr.leave.allocation'].create(vals)
                    for ovt in leave_type_overtime: 
                        ovt.update({
                                'state': 'approved'
                            })
