# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AttendanceRectification(models.Model):
    _inherit = 'hr.attendance.rectification'
    
    
    
    def action_send_rectification_data(self):
        for rectify in self:
            APPLICANT_ID = rectify.employee_id.barcode.lstrip("0")
            APPROVER_ID = rectify.employee_id.manager_id.barcode.lstrip("0")
            APP_DATE = rectify.app_date
            APP_REMARKS = 'Test'
            CMTMT_DATE = rectify.check_in
            CMTMT_DATE_TO = rectify.check_out
            CMTMT_STATUS = 'A'
            CMTMT_TIME_FROM = rectify.check_in.strftime('%H:%M:%S')
            CMTMT_TIME_TO = rectify.check_out.strftime('%H:%M:%S')
            CMTMT_TYPE =  ' '
            if rectify.partial == 'Partial':                
                CMTMT_TYPE =  'S'
            elif rectify.partial == 'Check In Time Missing':                
                CMTMT_TYPE =  'I'
            elif rectify.partial == 'Out Time Missing':                
                CMTMT_TYPE =  'I'
            elif rectify.partial == 'Full':                
                CMTMT_TYPE =  'S' 
            else:
                CMTMT_TYPE =  'M' 
                
            if rectify.partial == 'Check In Time Missing':                
                IO_TIME =  rectify.check_in.strftime('%H:%M:%S')
            elif rectify.partial == 'Out Time Missing':
                IO_TIME =  rectify.check_out.strftime('%H:%M:%S')                
            POST = 1
            shift_line = self.env['hr.shift.schedule.line'].search([('employee_id','=',rectify.employee_id.id),('date','=',rectify.date)])
            PREVIOUS_DAY_NIGHT_SHIFT = 'N'
            if shift_line:
                if shift_line.first_shift_id and shift_line.second_shift_id:
                    if shift_line.first_shift_id.shift_type == 'night' and shift_line.second_shift_id.shift_type == 'night':
                        PREVIOUS_DAY_NIGHT_SHIFT = 'Y'
                elif shift_line.first_shift_id:
                    if shift_line.first_shift_id.shift_type == 'night':
                        PREVIOUS_DAY_NIGHT_SHIFT = 'Y'
                elif shift_line.second_shift_id:
                    if shift_line.second_shift_id.shift_type == 'night':
                        PREVIOUS_DAY_NIGHT_SHIFT = 'Y'        
            REASON_CODE = ' '
            if rectify.partial == 'Check In Time Missing':               
                REASON_CODE = 50
            elif rectify.partial == 'Out Time Missing':                
                REASON_CODE = 51    
            elif  CMTMT_TYPE in ('S','M'): 
                REASON_CODE = 49    
            REMARKS = rectify.reason
            REQ_DATE = rectify.create_date  
            REQ_ID = rectify.id
            
            conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.7.153:1524/test3')
            cur = conn.cursor()
            statement = 'insert into ODOO_HR_COMMITMENT_SLIP_HEADER(APPLICANT_ID,APPROVER_ID, APP_DATE, APP_REMARKS,CMTMT_DATE,CMTMT_DATE_TO,CMTMT_STATUS,CMTMT_TIME_FROM,CMTMT_TIME_TO, CMTMT_TYPE, IO_TIME, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,: 14,:15,: 16,:17,: 18)'
            cur.execute(statement, (
            APPLICANT_ID,APPROVER_ID, APP_DATE, APP_REMARKS,CMTMT_DATE,CMTMT_DATE_TO,CMTMT_STATUS,CMTMT_TIME_FROM,CMTMT_TIME_TO, CMTMT_TYPE, IO_TIME, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID))
            conn.commit()
                        
            rectify.action_send_rectify_line_data(rectify.id)            
                        


    def action_send_rectify_line_data(self, rectify):
        rectification = self.env['hr.attendance.rectification'].search([('id','=',rectify)])
        for linerectify in rectification:
            CMTMT_DATE = linerectify.date
            REQ_ID = rectify          
            conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.7.153:1524/test3')
            cur = conn.cursor()
            statement = 'insert into ODOO_HR_COMMITMENT_SLIP_DETAIL(CMTMT_DATE,REQ_ID) values(: 2,:3)'
            cur.execute(statement, (CMTMT_DATE,REQ_ID))
            conn.commit()


