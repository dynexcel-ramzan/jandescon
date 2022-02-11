import json
from odoo import models
from odoo.exceptions import UserError


class ApprisalFeedback(models.AbstractModel):
    _name = 'report.de_apprisal_objective_report.feedback_xlx'
    _description = 'Apprisal report'
    _inherit = 'report.report_xlsx.abstract'
    
    
    
    def generate_xlsx_report(self, workbook, data, lines):
        data = self.env['hr.appraisal.feedback'].browse(self.env.context.get('active_ids'))
        format1 = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': False})
        sheet = workbook.add_worksheet('Appraisal Report')
        bold = workbook. add_format({'bold': True, 'align': 'center','border': True})
 
        sheet.set_column('A:B', 20,)
        sheet.set_column('C:D', 20,)
        sheet.set_column('E:F', 20,)
        sheet.set_column('G:H', 20,)
        sheet.set_column('I:J', 20,)
        sheet.set_column('K:L', 20,)
        
        sheet.write(1,0, 'Employee Number',bold)
        sheet.write(1,1, 'Employee' ,bold)
        sheet.write(1,2, 'Employee Status' ,bold) 
        sheet.write(1,3, 'Work location' ,bold)
        sheet.write(1,4, 'Department' ,bold)
        sheet.write(1,5, 'Performance Period',bold)
        sheet.write(1,6, 'Status',bold)
        sheet.write(1,7, 'Company',bold)
        sheet.write(1,8, 'Grade Type',bold)
        sheet.write(1,9, 'Employee Type',bold)
        sheet.write(1,10, 'Job Position',bold)
        sheet.write(1,11, 'Grade',bold)
        sheet.write(1,12, 'Mid Year Review Date',bold)
        sheet.write(1,13, 'End Year Review Date',bold)
        sheet.write(1,14, 'Company',bold)
        
        row = 3
        for line in lines: 
            employee_type = '-'
            if line.employee_id.emp_type=='permanent':
                employee_type = 'Regular'  
            if line.employee_id.emp_type=='contractor':
                employee_type = 'Contractual' 
            appraisal_status = '' 
            if line.state=='draft':
                appraisal_status = 'Employee Review'
            if line.state=='confirm':
                appraisal_status = 'Line Manager Review'
            if line.state=='sent':
                appraisal_status = 'Sent For Employee Review'
            if line.state=='sent':
                appraisal_status = 'Sent For Employee Review'       
            sheet.write(row, 0, line.emploee_code, format1)
            sheet.write(row, 1, line.employee_id.name, format1)
            sheet.write(row, 2, 'Active' if line.employee_id.active==True else 'In-Active', format1)
            sheet.write(row, 3, line.department_id.name, format1)
            sheet.write(row, 4, line.work_location_id.name, format1)
            sheet.write(row, 5, 'FY-2021-22', format1)  
            sheet.write(row, 6, str(appraisal_status), format1)
            sheet.write(row, 7, line.company_id.name, format1) 
            sheet.write(row, 8, line.grade_type_id.name, format1) 
            sheet.write(row, 9,  str(employee_type), format1)  
            sheet.write(row, 10, line.job_id.name, format1)
            sheet.write(row, 11, line.employee_id.grade_designation.name, format1) 
            sheet.write(row, 12, line.employee_id.mid_year_date, format1) 
            sheet.write(row, 13, line.employee_id.end_year_date, format1) 
            sheet.write(row, 12, line.company_id.name, format1)
            row += 1           