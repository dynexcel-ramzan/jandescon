from odoo import models, api, fields,_
from odoo.exceptions import UserError, ValidationError
from odoo.addons.resource.models.resource import HOURS_PER_DAY
import math

class PayslipOverTime(models.Model):
    _inherit = 'hr.payslip'
    
    def compute_sheet(self):
        for payslip in self:
            amount = 0 
            hours = 0 
            overtime_type = []
            work_entry_days = []
            overtime = self.env['hr.overtime.entry'].search([('employee_id', '=', payslip.employee_id.id),
                                                            ('company_id', '=', payslip.employee_id.company_id.id),('date','>=', payslip.date_from),('date','<=',payslip.date_to)])
            for type in overtime:
                overtime_type.append(type.overtime_type_id.id)
            uniq_overtime_type = set(overtime_type)
            for uniq_ovt_type in uniq_overtime_type:
                overtime_type = self.env['hr.overtime.type'].search([('id','=',uniq_ovt_type)], limit=1)
                overtime_work_entry_type = self.env['hr.work.entry.type'].search([('code','=',overtime_type.name)], limit=1)
                if not overtime_work_entry_type:
                    vals = {
                       'name' : overtime_type.name,
                       'code': overtime_type.name,
                       'sequence': 5,
                       'round_days' : 'FULL' ,
                           }
                    entry_type = self.env['hr.work.entry.type'].create(vals)
                    
                
            for uniq_overtime in uniq_overtime_type:
                uniq_amount = 0.0
                uniq_hours = 0.0
                uniq_overtime_entry = self.env['hr.overtime.entry'].search([('employee_id', '=', payslip.employee_id.id),
                                                                ('company_id', '=', payslip.employee_id.company_id.id),('date','>=', payslip.date_from),('date','<=',payslip.date_to),('overtime_type_id','=',uniq_overtime)])

                overtime_type = self.env['hr.overtime.type'].search([('id','=',uniq_overtime)], limit=1)
                overtime_work_entry_type = self.env['hr.work.entry.type'].search([('code','=',overtime_type.name)], limit=1)
                for uniq_ovt in uniq_overtime_entry:
                    uniq_amount = uniq_amount + uniq_ovt.amount    
                    uniq_hours = uniq_hours + uniq_ovt.overtime_hours  
                uniq_overtime_ids = [(0, 0, {
                                    'work_entry_type_id' : overtime_work_entry_type.id,
                                    'name': overtime_work_entry_type.name,
                                    'is_overtime': True,
                                    'sequence': overtime_work_entry_type.sequence,
                                    'number_of_days' : uniq_hours/(payslip.employee_id.shift_id.hours_per_day),
                                    'number_of_hours' : uniq_hours,
                                    'amount':  uniq_amount,
                                            })]
                work_days = self.env['hr.payslip.worked_days'].search([('payslip_id','=', payslip.id),('work_entry_type_id','=',overtime_work_entry_type.id)], limit=1)
                if not work_days:
                    payslip.worked_days_line_ids = uniq_overtime_ids     

                
            for ovt in overtime:
                amount = amount + ovt.amount        

            input_exists = self.env['hr.payslip.input'].search([('payslip_id', '=', payslip.id), ('code', '=', 'OT100')])

            if not input_exists:
                input_type_exists = self.env['hr.payslip.input.type'].search([('code', '=', 'OT100')])

                input_exists.create({
                                'input_type_id': input_type_exists.id,
                                'code': 'OT100',
                                'amount': amount,
                                'contract_id': payslip.contract_id.id,
                                'payslip_id': payslip.id,
                            })
            else:
                input_exists.write({
                    'amount':amount,
                })

        rec = super(PayslipOverTime, self).compute_sheet()
        return rec

    
    



    def action_payslip_done(self):
        """
        function used for marking paid overtime
        request.

        """
        for payslip in self:
            overtime = self.env['hr.overtime.request'].search([('employee_id', '=', payslip.employee_id.id),
                                                            ('state', '=', 'approved'),('date','>=', payslip.date_from),('date','<=',payslip.date_to)])
            for ovt in overtime:
                ovt.update({
                    'state': 'paid'
                })
        return super(PayslipOverTime, self).action_payslip_done()

        
        
        
        
class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days' 
    
    
    is_overtime = fields.Boolean(string='Is Overtime')
    
    
    @api.depends('is_paid', 'number_of_hours', 'payslip_id', 'payslip_id.normal_wage', 'payslip_id.sum_worked_hours')
    def _compute_amount(self):
        for worked_days in self:
            if not worked_days.contract_id:
                worked_days.amount = 0
                continue
            if worked_days.payslip_id.wage_type == "hourly":
                if worked_days.is_overtime != True:
                    worked_days.amount = worked_days.payslip_id.contract_id.hourly_wage * worked_days.number_of_hours if worked_days.is_paid else 0
            else:
                if worked_days.is_overtime != True:
                    worked_days.amount = worked_days.payslip_id.normal_wage * worked_days.number_of_hours / (worked_days.payslip_id.sum_worked_hours or 1) if worked_days.is_paid else 0

        