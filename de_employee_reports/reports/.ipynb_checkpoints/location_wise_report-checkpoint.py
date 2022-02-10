import json
from odoo import models
from odoo.exceptions import UserError

class EmployeeLocationwiseReport(models.AbstractModel):
    _name = 'report.de_employee_reports.location_wise_xlx'
    _description = 'HR Location Wise Report'
    _inherit = 'report.report_xlsx.abstract'
    
    
    def generate_xlsx_report(self, workbook, data, lines):
        data = self.env['ora.location.wise.wizard'].browse(self.env.context.get('active_ids'))
        format1 = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': False})
        format2 = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': False})
        sheet = workbook.add_worksheet('Employee Location Wise Report')
        bold = workbook. add_format({'bold': True, 'align': 'center','border': True})
        sheet.set_column('A:B', 10,)
        sheet.set_column('C:D', 20,)
        sheet.set_column('E:F', 20,)
        sheet.set_column('G:H', 20,)
        sheet.set_column('I:J', 20,)
        sheet.set_column('K:L', 20,)
        sheet.set_column('M:N', 30,)
        
        sheet.write(1,0, 'SR#',bold)
        sheet.write(1,1, 'Employee Number',bold)
        sheet.write(1,2, 'Employee' ,bold)
        sheet.write(1,3, 'Employee Type' ,bold)
        sheet.write(1,4, 'Staff Type' ,bold)
        sheet.write(1,5,'Job Position',bold)
        sheet.write(1,6,'Grade' ,bold)
        sheet.write(1,7, 'Department' ,bold)
        sheet.write(1,8, 'Work location' ,bold)
        sheet.write(1,9, 'Company' ,bold)
        row = 2
        record_count=0
        for location in data.work_location_ids:
            sheet.write(row, 1, str(location.name), bold)
            row += 1 
            location_employees= self.env['hr.employee'].search([('work_location_id','=', location.id)], order='emp_type desc')
            for location_employee in location_employees:
                sheet.write(row, 0, str(record_count), format1)
                sheet.write(row, 1, str(location_employee.emp_number), format1)
                sheet.write(row, 2, str(location_employee.name), format1)
                sheet.write(row, 3, str(location_employee.emp_type), format1)
                sheet.write(row, 4, str(location_employee.grade_type.name), format1)
                sheet.write(row, 5, str(location_employee.job_id.name if location_employee.job_id else '-'), format1)
                sheet.write(row, 6, str(location_employee.grade_designation.name if location_employee.grade_designation else '-'), format1)
                sheet.write(row, 7, str(location_employee.department_id.name if location_employee.department_id else '-'), format1)  
                sheet.write(row, 8, str(location_employee.work_location_id.name if location_employee.work_location_id else '-'), format1) 
                sheet.write(row, 9, str(location_employee.company_id.name), format1)
                row += 1 
                record_count += 1    