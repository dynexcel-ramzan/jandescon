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
        sheet.write(1,7, 'Grade Type',bold)
        sheet.write(1,8, 'Employee Type',bold)
        sheet.write(1,9, 'Job Position',bold)
        sheet.write(1,10, 'Grade',bold)
        sheet.write(1,11, 'Mid Year Review Date',bold)
        sheet.write(1,12, 'End Year Review Date',bold)
        sheet.write(1,13, 'Company',bold)
        
        row = 3
        for line in lines: 
            employee_type = '-'
            if line.name.emp_type=='permanent':
                employee_type = 'Regular'  
            if line.name.emp_type=='contractor':
                employee_type = 'Contractual' 
            appraisal_status = '' 
            if line.state=='draft':
                appraisal_status = 'Employee Review'
            if line.state=='confirm':
                appraisal_status = 'Line Manager Review'
            if line.state=='sent':
                appraisal_status = 'Sent For Employee Review'
            if line.state=='endorsed_employee':
                appraisal_status = 'Endorsed By Employee'
            if line.state=='endrosed_hod':
                appraisal_status = 'Endorsed By HOD'
            if line.state=='done':
                appraisal_status = 'Mid Year Close' 
            if line.state=='end_year_appraisee_review':
                appraisal_status = 'End Year Employee Review'
            if line.state=='end_year_appraiser_review':
                appraisal_status = 'End Year Line Manager Review'   
            if line.state=='end_year_sent_emp_view':
                appraisal_status = 'Sent of Employee Review'   
            if line.state=='end_year_endorse_hod':
                appraisal_status = 'Endorsed By HOD' 
            if line.state=='closed':
                appraisal_status = 'Closed'
            financial_year = 'FY-2021-22' 
            if line.end_year_date:
                financial_year = 'FY-'+str(int(line.end_year_date.strftime('%y'))-1)+' '+str(line.end_year_date.strftime('%y'))    
            sheet.write(row, 0, line.name.emp_number, format1)
            sheet.write(row, 1, line.name.name, format1)
            sheet.write(row, 2, 'Active' if line.name.active==True else 'In-Active', format1)
            sheet.write(row, 3, line.name.work_location_id.name, format1)
            sheet.write(row, 4, line.name.department_id.name, format1)
            sheet.write(row, 5, str(financial_year), format1)  
            sheet.write(row, 6, str(appraisal_status), format1)
            sheet.write(row, 7, line.name.grade_type.name, format1) 
            sheet.write(row, 8,  str(employee_type), format1)  
            sheet.write(row, 9, line.name.job_id.name, format1)
            sheet.write(row, 10, line.name.grade_designation.name, format1) 
            sheet.write(row, 11, line.mid_year_date.strftime('%d-%b-%Y') if line.mid_year_date else '-', format1) 
            sheet.write(row, 12, line.end_year_date.strftime('%d-%b-%Y') if line.end_year_date else '-', format1) 
            sheet.write(row, 13, line.name.company_id.name, format1)
            row += 1           