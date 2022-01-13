from odoo import models, fields, api, _
from  odoo import models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta


class EmployeeReportXlS(models.AbstractModel):
    _name = 'report.de_attendance_absent_days.absent_report_xlx'
    _description = 'Purchase report'
    _inherit = 'report.report_xlsx.abstract'
    
    def action_get_abset_days(self, data):
        absent_list = []
        company_data = ' '
        employees = []
        if  data.company_ids:
            employees = self.env['hr.employee'].sudo().search([('company_id','in', data.company_ids.ids)])
        elif data.employee_ids:
            employees = self.env['hr.employee'].sudo().search([('id','in', data.employee_ids.ids)])    
        sr_no = 1 
        for employee in employees:
            leave_status = ' '
            rectification_status = ' '
            is_leave_approved = 0
            remarks = ''
            delta_days = (data.date_to - data.date_from).days+1
            start_date = data.date_from
            for dayline in range(delta_days):
                if employee.date <= start_date:
                    is_holiday = False
                    remarks = ' '
                    current_shift = self.env['resource.calendar'].search([('company_id','=',employee.company_id.id)], limit=1)
                    if employee.shift_id:
                        current_shift = employee.shift_id
                    shift_line=self.env['hr.shift.schedule.line'].sudo().search([('employee_id','=',employee.id),('date','=',start_date),('state','=','posted')], limit=1)
                    if shift_line.first_shift_id:
                        current_shift = shift_line.first_shift_id
                    elif shift_line.second_shift_id:
                        current_shift = shift_line.second_shift_id
                    if shift_line.rest_day==True:
                        is_holiday = True
                    for gazetted_day in current_shift.global_leave_ids:
                        gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                        gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                        if str(start_date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(start_date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                            is_holiday = True
                    working_hours = 0
                    absent_category = False
                    if is_holiday == False:
                        attendances=self.env['hr.attendance'].search([('employee_id','=',employee.id),('att_date','=',start_date)])
                        leaves = self.env['hr.leave'].search([('employee_id','=',employee.id),('request_date_from','<=', start_date),('request_date_to','>=', start_date),('state','in',('confirm','validate'))])
                        rectification = self.env['hr.attendance.rectification'].search([('employee_id','=',employee.id),('check_in','<=', start_date),('check_out','>=', start_date),('state','in',('submitted','approved'))], limit=1)
                        leave_number_of_days = 0
                        leave_status = ''
                        for leave_day in leaves:
                            if leave_day.state=='validate':
                                leave_status = 'validate'
                            elif leave_day.state=='confirm':
                                leave_status = 'confirm'
                            leave_number_of_days += leave_day.number_of_days
                        for attendee in attendances:
                            working_hours += attendee.worked_hours
                        if   (working_hours > (current_shift.hours_per_day-1.5)):
                            pass
                        elif (working_hours < (current_shift.hours_per_day-1.5)) and (working_hours >(current_shift.hours_per_day/2)):
                            remarks = 'Half Present'
                            if is_holiday != True:
                                if rectification.state=='approved':
                                    pass
                                elif leave_status=='validate' and leave_number_of_days >= 0.5:
                                    pass
                                elif leave_status=='validate' and leave_number_of_days == 0.25:
                                    if working_hours < ((current_shift.hours_per_day/4)*3):
                                        absent_category = True
                                        remarks = 'Half Present (Leave[Approved] (0.25))'
                                    else:
                                        pass
                                elif rectification.state=='submitted':
                                    absent_category = True
                                    remarks = 'Half Present (Rectification [To Approve])'
                                elif not rectification and leave_status=='confirm':
                                    if leave_number_of_days >= 0.5:
                                        absent_category = True
                                        remarks = 'Half Present (Leave [To Approve] (0.5))'
                                    elif leave_number_of_days == 0.25:
                                        absent_category = True
                                        remarks = 'Half Present (Leave [To Approve] (0.25))'
                                else:
                                    absent_category = True
                        else:
                            if is_holiday == False:
                                if rectification.state=='approved':
                                    pass
                                elif leave_status and leave_number_of_days >= 1:
                                    pass
                                elif rectification.state=='submitted':
                                    absent_category = True
                                    remarks = 'Rectification (To Approve)'
                                elif leave_status=='confirm':
                                    if leave_number_of_days >= 1:
                                        absent_category = True
                                        remarks = 'Leave (To Approve)'
                                    elif leave_number_of_days >= 0.5:
                                        absent_category = True
                                        remarks = 'Half Leave (To Approve) (0.5)'
                                    elif leave_number_of_days >= 0.25:
                                        absent_category = True
                                        remarks = 'Short Leave (To Approve) (0.25)'
                                    else:
                                        absent_category = True 
                                elif leave_status=='validate':
                                    if leave_number_of_days >= 0.5:
                                        absent_category = True
                                        remarks = 'Half Leave (Approved) (0.5)'
                                    elif leave_number_of_days >= 0.25:
                                        absent_category = True
                                        remarks = 'Short Leave (Approved) (0.25)'   
                                    else:
                                        absent_category = True
                                else:
                                    absent_category = True
                        if absent_category==True:
                            absent_list.append({
                                'sr_no':  sr_no,
                                'employee': employee.name,
                                'emp_code': employee.emp_number,
                                'absent_on': start_date,
                                'remarks': remarks,
                            })
                            sr_no += 1
                start_date = (start_date + timedelta(1))
        return absent_list
    

    def generate_xlsx_report(self, workbook, data, lines):
        docs = self.env['absent.report.wizard'].browse(self.env.context.get('active_id'))
        sheet = workbook.add_worksheet('Absent Report')
        bold = workbook. add_format({'bold': True, 'align': 'center','bg_color': '#FFFF99','border': True})
        title = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 20, 'bg_color': '#FFFF99', 'border': True})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border':True})
        format2 = workbook.add_format({'align': 'center'})
        format3 = workbook.add_format({'align': 'center','bold': True,'border': True,})
        
        all_company_list = ' '
        for acompany in docs.company_ids:
            all_company_list =all_company_list + ' '+ str(acompany.name) 
            
        sheet.merge_range('A1:G2', str(all_company_list), format3)
        sheet.write('B3:B3','Date From', header_row_style)
        sheet.write('C3:C3',docs.date_from.strftime('%d-%b-%Y'), header_row_style)
        sheet.write('D3:D3','Date To', header_row_style)
        sheet.write('E3:E3',docs.date_to.strftime('%d-%b-%Y'), header_row_style)
        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 30)
        sheet.write(4,0,'Sr.#', header_row_style)
        sheet.write(4,1 , 'Employee name',header_row_style)
        sheet.write(4,2 , 'Employee code',header_row_style)
        sheet.write(4,3 , 'Absent on',header_row_style)
        sheet.write(4,4 , 'Remarks',header_row_style)
        absent_list = self.action_get_abset_days(docs)  
        row = 5
        for line in absent_list: 
            sheet.write(row, 0, line['sr_no'], format2)
            sheet.write(row, 1, line['employee'], format2)
            sheet.write(row, 2, line['emp_code'], format2)            
            sheet.write(row, 3, line['absent_on'].strftime('%d-%b-%y'), format2)            
            sheet.write(row, 4, line['remarks'])
            row += 1 