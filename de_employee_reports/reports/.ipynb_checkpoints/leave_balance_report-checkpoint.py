import json
from odoo import models
from odoo.exceptions import UserError

class EmployeeLeaveBalance(models.AbstractModel):
    _name = 'report.de_employee_reports.leave_balance_xlx'
    _description = 'Leave Balance Report'
    _inherit = 'report.report_xlsx.abstract'
    
    
    def generate_xlsx_report(self, workbook, data, lines):
        data = self.env['leave.balance.wizard'].browse(self.env.context.get('active_ids'))
        format1 = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': False})
        format2 = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': False})
        sheet = workbook.add_worksheet('Leave Balance Report')
        bold = workbook. add_format({'bold': True, 'align': 'center','border': True})
        sheet.set_column('A:B', 10,)
        sheet.set_column('C:D', 20,)
        sheet.set_column('E:F', 10,)
        sheet.set_column('G:H', 10,)
        sheet.set_column('I:J', 20,)
        sheet.set_column('K:L', 20,)
        sheet.set_column('M:N', 30,)
        
        sheet.write(0,0, 'SR#',bold)
        sheet.write(0,1, 'Employee Number',bold)
        sheet.write(0,2, 'Employee' ,bold)
        sheet.write(0,3, 'Leave Type',bold)
        sheet.write(0,4, 'Total',bold)
        sheet.write(0,5, 'Availed',bold)
        sheet.write(0,6, 'To Approve',bold)
        sheet.write(0,7, 'Balance',bold)
        sheet.write(0,8, 'Work location' ,bold)
        sheet.write(0,9, 'Department' ,bold)
        sheet.write(0,10,'Grade' ,bold)
        sheet.write(0,11,'Job Position',bold)
        sheet.write(0,12,'Company',bold)
        row = 1
        record_count=0
        for emp in data.employee_ids:
            leave_allocation = self.env['hr.leave.allocation'].search([('employee_id','=',emp.id),('fiscal_year','=',data.fiscal_year_id.name)])
            for line in leave_allocation:
                leave_count = 0
                leaves_toapprove=self.env['hr.leave'].search([('employee_id','=',line.employee_id.id),('holiday_status_id','=',line.id),('state','=','confirm')])
                for leave_count in leaves_toapprove:
                    leave_count += leave_count.number_of_days   
                sheet.write(row, 0, str(record_count), format1)
                sheet.write(row, 1, str(line.employee_id.emp_number), format1)
                sheet.write(row, 2, str(line.employee_id.name), format1)
                sheet.write(row, 3, str(line.holiday_status_id.name), format1)
                sheet.write(row, 4, str(line.max_leaves), format1)
                sheet.write(row, 5, str(line.leaves_taken), format1) 
                sheet.write(row, 6, str(round(leave_count,2)), format2)
                sheet.write(row, 7, str(round((line.max_leaves-(line.leaves_taken+leave_count)),2)), format1) 
                sheet.write(row, 8, str(emp.work_location_id.name if emp.work_location_id else '-'), format1) 
                sheet.write(row, 9, str(emp.department_id.name if emp.department_id else '-'), format1)  
                sheet.write(row, 10, str(emp.grade_designation.name if emp.grade_designation else '-'), format1)
                sheet.write(row, 11, str(emp.job_id.name if emp.job_id else '-'), format1)
                sheet.write(row, 12, str(emp.company_id.name), format1)
                row += 1 
                record_count += 1