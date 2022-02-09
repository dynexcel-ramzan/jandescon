# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

class HrExpense(models.Model):
    _inherit = 'hr.expense'
    
    member_id = fields.Many2one('hr.employee.family', string='Dependent', domain="[('employee_id','=',employee_id)]")
    meter_reading = fields.Float(string='Meter Reading')
    fleet_id = fields.Many2one('vehicle.meter.detail', string='Vehicle')
    attachment_id = fields.Many2many('ir.attachment', relation="files_rel_expense",
                                            column1="doc_id",
                                            column2="attachment_id",
                                            string="Attachment")
    sub_category_id = fields.Many2one('expense.sub.category', string='Expense Sub-Category', required=True, copy=True)
    sheet_line_id = fields.Many2one('hr.expense.sheet.line', string='Sheet Lines')
    percentage = fields.Float(string='Percentage')
    
    @api.onchange('product_id', 'date', 'account_id')
    def _onchange_product_id_date_account_id(self):
        rec = self.env['account.analytic.default'].sudo().account_get(
            product_id=self.product_id.id,
            account_id=self.account_id.id,
            company_id=self.company_id.id,
            date=self.date
        )
        
    
    @api.model
    def create(self, vals):
        sheet = super(HrExpense, self).create(vals)
#         sheet.action_check_attachment()
        return sheet
    
    
    
    
    @api.constrains('meter_reading')
    def _check_meter_reading(self):
        for line in self:
            if line.fleet_id:
                if line.fleet_id.id!=line.employee_id.vehicle_id.id:
                    raise UserError('You are not allow to select Vehicle rather than '+str(line.employee_id.vehicle_id.name))
                    
            if line.meter_reading >= 0.0 and line.product_id.meter_reading>=0.0:
                opening_vehicle_balance = 0
                for reading_line  in line.employee_id.vehicle_meter_line_ids:
                    if line.sub_category_id.id==reading_line.sub_category_id.id:
                        opening_vehicle_balance = reading_line.opening_reading
                if opening_vehicle_balance <= line.meter_reading:
                    current_reading = line.meter_reading + opening_vehicle_balance 
                    if line.sheet_id.exception!=True:
                        if current_reading >= (line.sub_category_id.meter_reading + opening_vehicle_balance):
                            pass
                        else:
                            raise UserError(_('Your Vehicle meter reading does not reach to limit. Current Reading ' +str(current_reading)+' Difference with opening balance less than limit! '+str(line.product_id.meter_reading)+' your previous opening reading is '+str(opening_vehicle_balance)))
                else:
                    raise UserError(_('You are entering reading '+str(line.meter_reading)+' less than your previous opening reading is '+str(opening_vehicle_balance)))
                    
                    
                    
class MailMessage(models.Model):
    _inherit = 'mail.message'                    