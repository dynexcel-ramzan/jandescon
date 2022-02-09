# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import cx_Oracle
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

class AttendanceRectification(models.Model):
    _inherit = 'hr.attendance.rectification'

    is_posted = fields.Boolean(string='Post to Oracle')
    
    def action_send_rectification_data_fetch(self):
        conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')    
        cur = conn.cursor()
        statement = 'select * from ODOO_HR_COMMITMENT_SLIP_HEADER'
        cur.execute(statement)
        comitment_data = cur.fetchall()
        cstatement = 'select count(*) from ODOO_HR_COMMITMENT_SLIP_HEADER'
        cur.execute(cstatement)
        ccomitment_data = cur.fetchall()   
        dstatement = 'select * from ODOO_HR_COMMITMENT_SLIP_DETAIL'
        cur.execute(dstatement)
        dcomitment_data = cur.fetchall()
        raise UserError('Count '+str(ccomitment_data )+'  '+str(comitment_data)+'     Detail Data '+str(dcomitment_data))

    def action_re_send_rectification_data(self):
        rectifications = self.env['hr.attendance.rectification'].search([('is_posted','!=',True),('state','=','approved'),('date','>','2021-07-15')], limit=100)
        for rectify in self:
            if rectify.is_posted == True and rectify.state =='approved':
                conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                cur = conn.cursor()
                statement = """select * from ODOO_HR_COMMITMENT_SLIP_HEADER where APP_REMARKS=""" + str(
                    rectify.id) + """ """
                cur.execute(statement)
                already_exist_data = cur.fetchall()
                if already_exist_data:
                    pass
                else:
                    if rectify.employee_id.barcode and rectify.employee_id.parent_id.barcode:
                        APPLICANT_ID = rectify.employee_id.barcode.lstrip("0")
                        APPROVER_ID = rectify.employee_id.parent_id.barcode.lstrip("0")
                        APP_DATE = rectify.app_date if rectify.app_date else fields.date.today()
                        APP_REMARKS = str(rectify.id)
                        CMTMT_DATE = rectify.date
                        CMTMT_DATE_TO = rectify.check_out
                        CMTMT_TIME_TO = rectify.check_out
                        if rectify.check_out:
                            CMTMT_DATE_TO = rectify.check_out + relativedelta(hours =+ 5)
                            CMTMT_TIME_TO = rectify.check_out + relativedelta(hours=+ 5)
                        CMTMT_STATUS =  ' '
                        if rectify.state == 'approved':
                            CMTMT_STATUS = 'A'
                        CMTMT_TIME_FROM = rectify.check_in
                        if rectify.check_in:
                            CMTMT_TIME_FROM = rectify.check_in + relativedelta(hours =+ 5)

                        CMTMT_TYPE =  ' '
                        if rectify.partial == 'Partial':
                            CMTMT_TYPE =  'S'
                        elif rectify.partial == 'Check In Time Missing':
                            CMTMT_TYPE =  'I'
                        elif rectify.partial == 'Out Time Missing':
                            CMTMT_TYPE =  'I'
                        elif rectify.partial == 'Full':
                            if   rectify.number_of_Days >= 1:
                                CMTMT_TYPE =  'M'
                            else:
                                CMTMT_TYPE =  'M'
                        else:
                            CMTMT_TYPE =  'M'

                        POST = 1
                        shift_line = self.env['hr.shift.schedule.line'].search([('employee_id','=',rectify.employee_id.id),('date','=',rectify.date)], limit=1)
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
                        REQ_DATE = rectify.create_date if  rectify.create_date else fields.date.today()
                        REQ_ID = rectify.id
                        LOG_ID = rectify.id
                        if  rectify.partial == 'Check In Time Missing':
                            IO_TIME =  rectify.check_in + relativedelta(hours =+ 5)
                            conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                            cur = conn.cursor()
                            statement = 'insert into ODOO_HR_COMMITMENT_SLIP_HEADER(APPLICANT_ID,IO_TIME,APPROVER_ID,APP_DATE,CMTMT_DATE,CMTMT_DATE_TO, APP_REMARKS,CMTMT_STATUS, CMTMT_TYPE, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID,LOG_ID) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,:14,:15,:16,:17)'
                            cur.execute(statement, (
                                                                               APPLICANT_ID,IO_TIME,APPROVER_ID,APP_DATE,CMTMT_DATE,CMTMT_DATE_TO, APP_REMARKS,CMTMT_STATUS, CMTMT_TYPE, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID,LOG_ID))
                            conn.commit()
                        elif rectify.partial == 'Out Time Missing':
                            IO_TIME =  rectify.check_out + relativedelta(hours =+ 5)
                            conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                            cur = conn.cursor()
                            statement = 'insert into ODOO_HR_COMMITMENT_SLIP_HEADER(APPLICANT_ID,IO_TIME,APPROVER_ID,APP_DATE,CMTMT_DATE,CMTMT_DATE_TO, APP_REMARKS,CMTMT_STATUS, CMTMT_TYPE, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID,LOG_ID) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,:14,:15,:16,:17)'
                            cur.execute(statement, (
                                                                                APPLICANT_ID,IO_TIME,APPROVER_ID,APP_DATE,CMTMT_DATE,CMTMT_DATE_TO,APP_REMARKS,CMTMT_STATUS, CMTMT_TYPE, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID,LOG_ID))
                            conn.commit()
                        elif rectify.partial == 'Partial':

                            conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                            cur = conn.cursor()
                            statement = 'insert into ODOO_HR_COMMITMENT_SLIP_HEADER(APPLICANT_ID,APPROVER_ID,APP_DATE,CMTMT_DATE,CMTMT_DATE_TO,CMTMT_TIME_FROM,CMTMT_TIME_TO, APP_REMARKS,CMTMT_STATUS, CMTMT_TYPE, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID,LOG_ID) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,:14,:15,:16,:17,:18)'
                            cur.execute(statement, (
                                                                               APPLICANT_ID,APPROVER_ID,APP_DATE,CMTMT_DATE,CMTMT_DATE_TO,  CMTMT_TIME_FROM,CMTMT_TIME_TO,APP_REMARKS,CMTMT_STATUS, CMTMT_TYPE, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID,LOG_ID))
                            conn.commit()
                        else:
                            conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                            cur = conn.cursor()
                            statement = 'insert into ODOO_HR_COMMITMENT_SLIP_HEADER(APPLICANT_ID,APPROVER_ID,APP_DATE,CMTMT_DATE,CMTMT_DATE_TO, APP_REMARKS,CMTMT_STATUS, CMTMT_TYPE, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID,LOG_ID) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,:14,:15,:16)'
                            cur.execute(statement, (
                                                                               APPLICANT_ID,APPROVER_ID,APP_DATE,CMTMT_DATE,CMTMT_DATE_TO, APP_REMARKS,CMTMT_STATUS, CMTMT_TYPE, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID,LOG_ID))
                            conn.commit()

                        rectify.action_send_rectify_line_data(rectify.id)
                        rectify.is_posted = True


    def action_send_rectification_data(self):
        rectifications = self.env['hr.attendance.rectification'].search([('is_posted','!=',True),('state','=','approved'),('date','>','2021-07-15')], limit=100)
        for rectify in rectifications:
            if rectify.is_posted == False and rectify.state =='approved':
                if rectify.employee_id.barcode and rectify.employee_id.parent_id.barcode:
                    APPLICANT_ID = rectify.employee_id.barcode.lstrip("0")
                    APPROVER_ID = rectify.employee_id.parent_id.barcode.lstrip("0")
                    APP_DATE = rectify.app_date if rectify.app_date else fields.date.today()
                    APP_REMARKS = str(rectify.id)
                    CMTMT_DATE = rectify.date
                    CMTMT_DATE_TO = rectify.check_out
                    CMTMT_TIME_TO = rectify.check_out
                    if rectify.check_out:
                        CMTMT_DATE_TO = rectify.check_out + relativedelta(hours =+ 5)
                        CMTMT_TIME_TO = rectify.check_out + relativedelta(hours=+ 5)
                    CMTMT_STATUS =  ' '
                    if rectify.state == 'approved':
                        CMTMT_STATUS = 'A'
                    CMTMT_TIME_FROM = rectify.check_in
                    if rectify.check_in:
                        CMTMT_TIME_FROM = rectify.check_in + relativedelta(hours =+ 5)

                    CMTMT_TYPE =  ' '
                    if rectify.partial == 'Partial':
                        CMTMT_TYPE =  'S'
                    elif rectify.partial == 'Check In Time Missing':
                        CMTMT_TYPE =  'I'
                    elif rectify.partial == 'Out Time Missing':
                        CMTMT_TYPE =  'I'
                    elif rectify.partial == 'Full':
                        if   rectify.number_of_Days >= 1:
                            CMTMT_TYPE =  'M'
                        else:
                            CMTMT_TYPE =  'M'
                    else:
                        CMTMT_TYPE =  'M'

                    POST = 1
                    shift_line = self.env['hr.shift.schedule.line'].search([('employee_id','=',rectify.employee_id.id),('date','=',rectify.date)], limit=1)
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
                    REQ_DATE = rectify.create_date if  rectify.create_date else fields.date.today()
                    REQ_ID = rectify.id
                    LOG_ID = rectify.id
                    if  rectify.partial == 'Check In Time Missing':
                        IO_TIME =  rectify.check_in + relativedelta(hours =+ 5)
                        conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                        cur = conn.cursor()
                        statement = 'insert into ODOO_HR_COMMITMENT_SLIP_HEADER(APPLICANT_ID,IO_TIME,APPROVER_ID,APP_DATE,CMTMT_DATE,CMTMT_DATE_TO, APP_REMARKS,CMTMT_STATUS, CMTMT_TYPE, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID,LOG_ID) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,:14,:15,:16,:17)'
                        cur.execute(statement, (
                                                                           APPLICANT_ID,IO_TIME,APPROVER_ID,APP_DATE,CMTMT_DATE,CMTMT_DATE_TO, APP_REMARKS,CMTMT_STATUS, CMTMT_TYPE, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID,LOG_ID))
                        conn.commit()
                    elif rectify.partial == 'Out Time Missing':
                        IO_TIME =  rectify.check_out + relativedelta(hours =+ 5)
                        conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                        cur = conn.cursor()
                        statement = 'insert into ODOO_HR_COMMITMENT_SLIP_HEADER(APPLICANT_ID,IO_TIME,APPROVER_ID,APP_DATE,CMTMT_DATE,CMTMT_DATE_TO, APP_REMARKS,CMTMT_STATUS, CMTMT_TYPE, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID,LOG_ID) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,:14,:15,:16,:17)'
                        cur.execute(statement, (
                                                                            APPLICANT_ID,IO_TIME,APPROVER_ID,APP_DATE,CMTMT_DATE,CMTMT_DATE_TO,APP_REMARKS,CMTMT_STATUS, CMTMT_TYPE, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID,LOG_ID))
                        conn.commit()
                    elif rectify.partial == 'Partial':

                        conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                        cur = conn.cursor()
                        statement = 'insert into ODOO_HR_COMMITMENT_SLIP_HEADER(APPLICANT_ID,APPROVER_ID,APP_DATE,CMTMT_DATE,CMTMT_DATE_TO,CMTMT_TIME_FROM,CMTMT_TIME_TO, APP_REMARKS,CMTMT_STATUS, CMTMT_TYPE, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID,LOG_ID) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,:14,:15,:16,:17,:18)'
                        cur.execute(statement, (
                                                                           APPLICANT_ID,APPROVER_ID,APP_DATE,CMTMT_DATE,CMTMT_DATE_TO,  CMTMT_TIME_FROM,CMTMT_TIME_TO,APP_REMARKS,CMTMT_STATUS, CMTMT_TYPE, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID,LOG_ID))
                        conn.commit()
                    else:
                        conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                        cur = conn.cursor()
                        statement = 'insert into ODOO_HR_COMMITMENT_SLIP_HEADER(APPLICANT_ID,APPROVER_ID,APP_DATE,CMTMT_DATE,CMTMT_DATE_TO, APP_REMARKS,CMTMT_STATUS, CMTMT_TYPE, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID,LOG_ID) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,:14,:15,:16)'
                        cur.execute(statement, (
                                                                           APPLICANT_ID,APPROVER_ID,APP_DATE,CMTMT_DATE,CMTMT_DATE_TO, APP_REMARKS,CMTMT_STATUS, CMTMT_TYPE, POST, PREVIOUS_DAY_NIGHT_SHIFT, REASON_CODE, REMARKS, REQ_DATE, REQ_ID,LOG_ID))
                        conn.commit()

                    rectify.action_send_rectify_line_data(rectify.id)
                    rectify.is_posted = True


    def action_send_rectify_line_data(self, rectify):
        rectification = self.env['hr.attendance.rectification'].search([('id','=',rectify)])
        for linerectify in rectification:
            if linerectify.number_of_Days >=1:
                count_run = linerectify.number_of_Days + 1 
                for day in range(round(count_run)):
                    CMTMT_DATE = linerectify.date + timedelta(day)
                    REQ_ID = linerectify.id          
                    conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                    cur = conn.cursor()
                    statement = 'insert into ODOO_HR_COMMITMENT_SLIP_DETAIL(CMTMT_DATE,REQ_ID) values(: 2,:3)'
                    cur.execute(statement, (CMTMT_DATE,REQ_ID))
                    conn.commit()
            else:
                CMTMT_DATE = linerectify.date if linerectify.date else fields.date.today()
                REQ_ID = linerectify.id          
                conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                cur = conn.cursor()
                statement = 'insert into ODOO_HR_COMMITMENT_SLIP_DETAIL(CMTMT_DATE,REQ_ID) values(: 2,:3)'
                cur.execute(statement, (CMTMT_DATE,REQ_ID))
                conn.commit()


