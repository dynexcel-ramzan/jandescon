# -*- coding: utf-8 -*-

from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.resource.models.resource import HOURS_PER_DAY


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'
    
    number_of_hours_calc = fields.Float(
        'Duration (hours)',
        help="If Accrual Allocation: Number of hours allocated in addition to the ones you will get via the accrual' system.")
    
    approval_request_id = fields.Many2one('approval.request', string="Approval")
    category_id = fields.Many2one('approval.category', string="Approval Category")
    overtime_id = fields.Many2one('hr.overtime.request', string="Overtime")
    ovt_date =  fields.Date(string='Overtime CPL Date')
    request_date = fields.Date(string='Request Date')
    
    
    
    def cron_expire_allocation(self):
        for line in self:
            if line.overtime_id:
                if line.overtime_id.overtiem_type_id.type == 'rest_day':
                    rest_diff = fields.date.today() - line.request_date
                    if rest_diff > 21:
                        line.action_refuse()
                elif line.overtime_id.overtiem_type_id.type == 'gazetted':
                    gazetted_diff = fields.date.today() - line.request_date
                    if gazetted_diff > 90:
                        line.action_refuse()
            

    
    @api.model
    def create(self, values):
        """ Override to avoid automatic logging of creation """
        employee_id = values.get('employee_id', False)
        if not values.get('department_id'):
            values.update({'department_id': self.env['hr.employee'].browse(employee_id).department_id.id})
        holiday = super(HrLeaveAllocation, self.with_context(mail_create_nosubscribe=True)).create(values)
        holiday.add_follower(employee_id)
        if holiday.validation_type == 'hr':
            holiday.message_subscribe(partner_ids=(holiday.employee_id.parent_id.user_id.partner_id | holiday.employee_id.leave_manager_id.partner_id).ids)
        if not self._context.get('import_file'):

            holiday.activity_update()
            
        return holiday
    
   
    def action_create_approval_request_allocation(self):
        approver_ids  = []        
        request_list = []
        for line in self:
            if line.employee_id.parent_id.user_id:
                approval_category =self.env['approval.category'].sudo().search([('company_id','=',line.employee_id.company_id.id),('name','=','Leave Allocation')], limit=1)
                if not approval_category:
                    category = {
                    'name': 'Leave Allocation',
                    'company_id': line.employee_id.company_id.id,
                    'is_parent_approver': True,
                    }
                    approval_category = self.env['approval.category'].sudo().create(category)
                request_list.append({
                        'name':  str(line.employee_id.name ),
                        'request_owner_id': line.employee_id.user_id.id,
                        'category_id': approval_category.id,
                        'allocation_id': line.id,
                            'reason': ' Days: ' + str(line.number_of_days_display)+"\n" + ' Remarks:   ' +str(line.name)+"\n",
                        'request_status': 'new',
                })
                approval_request_id = self.env['approval.request'].create(request_list)
                approval_request_id._onchange_category_id()
                approval_request_id.action_confirm()
                approval_request_id.action_date_confirm_update()
                line.approval_request_id = approval_request_id.id
                line.category_id = approval_category.id


    
    
    @api.depends('number_of_days', 'employee_id')
    def _compute_number_of_hours_display(self):
        for allocation in self:
            if allocation.parent_id and allocation.parent_id.type_request_unit == "hour":
                allocation.number_of_hours_display = allocation.number_of_days * HOURS_PER_DAY
            elif allocation.number_of_days:
                allocation.number_of_hours_display = allocation.number_of_days * (allocation.employee_id.sudo().resource_id.calendar_id.hours_per_day or HOURS_PER_DAY)
            else:
                allocation.number_of_hours_display = 0.0
                
            if allocation.number_of_hours_calc > 0.0:
                allocation.number_of_hours_display = allocation.number_of_hours_calc    
                
   
