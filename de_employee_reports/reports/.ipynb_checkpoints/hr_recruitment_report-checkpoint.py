import json
from odoo import models
from odoo.exceptions import UserError

class EmployeeRecruitment(models.AbstractModel):
    _name = 'report.de_employee_reports.recruitment_xlx'
    _description = 'HR Recruitment Report'
    _inherit = 'report.report_xlsx.abstract'
    
    
    def generate_xlsx_report(self, workbook, data, lines):
        data = self.env['ora.recruitment.wizard'].browse(self.env.context.get('active_ids'))
        format1 = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': False})
        format2 = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': False})
        sheet = workbook.add_worksheet('Employee Hirring Report')
        bold = workbook. add_format({'bold': True, 'align': 'center','border': True})
        sheet.set_column('A:B', 10,)
        sheet.set_column('C:D', 20,)
        sheet.set_column('E:F', 20,)
        sheet.set_column('G:H', 20,)
        sheet.set_column('I:J', 20,)
        sheet.set_column('K:L', 20,)
        sheet.set_column('M:N', 30,)
        sheet.write(0,3,str(data.start_date.strftime('%d-%b-%Y')),bold)
        sheet.write(0,5,str(data.end_date.strftime('%d-%b-%Y')),bold)
        employees=self.env['hr.employee'].search([('date','>=',data.start_date),('date','<=',data.end_date),('company_id','=',data.company_id.id)], order='emp_type desc')
        sheet.write(1,0, 'SR#',bold)
        sheet.write(1,1, 'Employee Number',bold)
        sheet.write(1,2, 'Employee' ,bold)
        sheet.write(1,3, 'Employee Type' ,bold)
        sheet.write(1,4, 'Grade Type' ,bold)
        sheet.write(1,5,'Job Position',bold)
        sheet.write(1,6,'Grade' ,bold)
        sheet.write(1,7, 'Department' ,bold)
        sheet.write(1,8, 'Work location' ,bold)
        sheet.write(1,9, 'Company' ,bold)
        row = 2
        record_count=0
        for line in employees:
            sheet.write(row, 0, str(record_count), format1)
            sheet.write(row, 1, str(line.emp_number), format1)
            sheet.write(row, 2, str(line.name), format1)
            sheet.write(row, 3, str(line.emp_type), format1)
            sheet.write(row, 4, str(line.grade_type.name), format1)
            sheet.write(row, 5, str(line.job_id.name if line.job_id else '-'), format1)
            sheet.write(row, 6, str(line.grade_designation.name if line.grade_designation else '-'), format1)
            sheet.write(row, 7, str(line.department_id.name if line.department_id else '-'), format1)  
            sheet.write(row, 8, str(line.work_location_id.name if line.work_location_id else '-'), format1) 
            sheet.write(row, 9, str(line.company_id.name), format1)
            row += 1 
            record_count += 1