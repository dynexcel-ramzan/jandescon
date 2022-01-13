import json
from odoo import models
from odoo.exceptions import UserError


class ApprisalReportXlS(models.AbstractModel):
    _name = 'report.de_apprisal_objective_report.apprisal_report_xlx'
    _description = 'Apprisal objective report'
    _inherit = 'report.report_xlsx.abstract'
    
    
    
    def generate_xlsx_report(self, workbook, data, lines):
        data = self.env['hr.appraisal.objective'].browse(self.env.context.get('active_ids'))
        format1 = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': False})
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
        sheet.write(1,5, 'states',bold)
        sheet.write(1,6, 'company',bold)
        sheet.write(1,7, 'Grade Type',bold)
        sheet.write(1,8, 'Employee Type',bold)
        sheet.write(1,9, 'Job Position',bold)
        sheet.write(1,10, 'Grade',bold)
        sheet.write(1,11, 'Remarks',bold)
        
        row = 3
        Apprisal_objective = self.env['hr.appraisal.objective'].search([])
        for line in lines: 
            
            sheet.write(row, 0, line.emploee_code, format1)
            sheet.write(row, 1, line.employee_id.name, format1)
            sheet.write(row, 2, line.department_id.name, format1)
            sheet.write(row, 3, line.work_location_id.name, format1)
            sheet.write(row, 4, line.objective_year, format1)  
            sheet.write(row, 5, line.state, format1)
            sheet.write(row, 6, line.company_id.name, format1) 
            sheet.write(row, 7, line.grade_type_id.name, format1) 
            sheet.write(row, 8, line.employee_id.emp_type, format1)  
            sheet.write(row, 9, line.job_id.name, format1)
            sheet.write(row, 10, line.employee_id.grade_designation.name, format1) 
            sheet.write(row, 11, line.description, format1)
            row += 1           