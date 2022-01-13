# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    
    
    def action_view_wfh_attendance_data(self):
         
        conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.152:1521/PROD')    
        cur = conn.cursor()
        statement = 'select * from ODOO_ATTEND_DATA'
        cur.execute(statement)
        comitment_data = cur.fetchall()
        cstatement = 'select count(*) from ODOO_ATTEND_DATA'
        cur.execute(cstatement)
        ccomitment_data = cur.fetchall()
        
        raise UserError('Count '+str(ccomitment_data)+' '+str(comitment_data))
    
    
    def action_send_wfh_attendance_data(self):    
        for wfh in self:
            if wfh.remarks == 'WFH(Work From Home)':
                ATT_DATE = str(wfh.att_date)
                ATT_TIME = wfh.check_in.strftime('%H%M%S')
                CARD_NO = leave.employee_id.barcode
                CREATION_DATE = wfh.check_in
                MAC_NUMBER = 48
                REMARKS = wfh.remarks
                UPDATION_DATE = fields.datetime.today()
                conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.7.8.152:1521/PROD')
                cur = conn.cursor()
                statement = 'insert into ODOO_ATTEND_DATA(ATT_DATE,ATT_TIME, CARD_NO, CREATION_DATE, MAC_NUMBER,REMARKS,UPDATION_DATE) values(: 2,:3,: 4,:5,: 6,:7,: 8)'
                cur.execute(statement, (
                     ATT_DATE,ATT_TIME, CARD_NO, CREATION_DATE, MAC_NUMBER,REMARKS,UPDATION_DATE))
                conn.commit()