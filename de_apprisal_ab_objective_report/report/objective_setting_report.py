import json
from odoo import models
from odoo.exceptions import UserError


class ApprisalReportXlS(models.AbstractModel):
    _name = 'report.de_apprisal_ab_objective_report.apprisal_ab_rept_xlx'
    _description = 'Absent objective report'
    _inherit = 'report.report_xlsx.abstract'
    
    
    
    def generate_xlsx_report(self, workbook, data, lines):
        data = self.env['hr.appraisal.objective'].browse(self.env.context.get('active_ids'))
        format1 = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': False})
        format2 = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': False})
        sheet = workbook.add_worksheet('Apprisal objective report')
        bold = workbook. add_format({'bold': True, 'align': 'center','border': True})
        
        
        sheet.set_column('A:B', 20,)
        sheet.set_column('C:D', 20,)
        sheet.set_column('E:F', 20,)
        sheet.set_column('G:H', 20,)
        sheet.set_column('I:J', 20,)
        sheet.set_column('K:L', 20,)
        
        

        
        
        sheet.write(1,0, 'Employee Number',bold)
        sheet.write(1,1, 'Employee' ,bold)
        sheet.write(1,2, 'Work location' ,bold)
        sheet.write(1,3, 'Department' ,bold)
        sheet.write(1,4, 'objective year',bold)
        sheet.write(1,5, 'Remarks',bold)
        sheet.write(1,6, 'company',bold)
        sheet.write(1,7, 'Grade Type',bold)
        sheet.write(1,8, 'Employee Type',bold)
        sheet.write(1,9, 'Job Position',bold)
        sheet.write(1,10, 'Grade',bold)
        
        
        row = 3
        employees = self.env['hr.employee'].search([('active','=',True)])
        for emp in employees:
            Apprisal_objective = self.env['hr.appraisal.objective'].search([('employee_id','=',emp.id)])
            if not Apprisal_objective:
                sheet.write(row, 0, emp.emp_number, format1)
                sheet.write(row, 1, emp.name, format1)
                sheet.write(row, 2, emp.department_id.name, format1)
                sheet.write(row, 3, emp.work_location_id.name, format1)
                sheet.write(row, 4, 'FY-2021-22', format1)  
                sheet.write(row, 5, 'Objective Not Created', format2)
                sheet.write(row, 6, emp.company_id.name, format1) 
                sheet.write(row, 7, emp.grade_type.name, format1) 
                sheet.write(row, 8, emp.emp_type, format1)  
                sheet.write(row, 9, emp.job_id.name, format1)
                sheet.write(row, 10, emp.grade_designation.name, format1) 
                row += 1           