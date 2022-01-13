# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

import cx_Oracle


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    wfh_posted = fields.Boolean(string='WFH post to Oracle')
    
    
    
    def action_view_wfh_attendance_data(self):
         
        conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')    
        cur = conn.cursor()
        statement = 'select * from ODOO_ATTEND_DATA'
        cur.execute(statement)
        comitment_data = cur.fetchall()
        cstatement = 'select count(*) from ODOO_ATTEND_DATA'
        cur.execute(cstatement)
        ccomitment_data = cur.fetchall()
        
        raise UserError('Count '+str(ccomitment_data)+' '+str(comitment_data))
    
    
    def action_send_wfh_attendance_data(self):
        unreconcile_wfh = self.env['hr.attendance'].search([('wfh_posted','=',False),('remarks','=','WFH(Work From Home)')])     
        for wfh in unreconcile_wfh:
            if wfh.remarks == 'WFH(Work From Home)' and wfh.wfh_posted==False:
                if wfh.check_in:
                    ATT_DATE = str(wfh.att_date)
                    if wfh.att_date: 
                        ATT_DATE = str(wfh.att_date.strftime('%m/%d/%Y'))
                    att_time = wfh.check_in + relativedelta(hours =+ 5) 
                    ATT_TIME = att_time.strftime('%H%M%S')
                    CARD_NO = wfh.employee_id.barcode
                    CREATION_DATE = wfh.check_in + relativedelta(hours =+ 5)
                    MAC_NUMBER = 48
                    REMARKS = wfh.remarks
                    UPDATION_DATE = fields.datetime.today()
                    conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                    cur = conn.cursor()
                    statement = 'insert into ODOO_ATTEND_DATA(ATT_DATE,ATT_TIME, CARD_NO, CREATION_DATE, MAC_NUMBER,REMARKS,UPDATION_DATE) values(: 2,:3,: 4,:5,: 6,:7,: 8)'
                    cur.execute(statement, (
                     ATT_DATE,ATT_TIME, CARD_NO, CREATION_DATE, MAC_NUMBER,REMARKS,UPDATION_DATE))
                    conn.commit()
                    wfh.update({
                    'wfh_posted': True
                    })
      
                if wfh.check_out:
                    ATT_DATE = str(wfh.att_date)
                    if wfh.att_date:  
                        ATT_DATE = str(wfh.att_date.strftime('%m/%d/%Y'))
                    out_time = wfh.check_out + relativedelta(hours =+ 5)
                    ATT_TIME = out_time.strftime('%H%M%S')
                    CARD_NO = wfh.employee_id.barcode
                    CREATION_DATE = wfh.check_out + relativedelta(hours =+ 5)
                    MAC_NUMBER = 49
                    REMARKS = wfh.remarks
                    UPDATION_DATE = fields.datetime.today()
                    conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                    cur = conn.cursor()
                    statement = 'insert into ODOO_ATTEND_DATA(ATT_DATE,ATT_TIME, CARD_NO, CREATION_DATE, MAC_NUMBER,REMARKS,UPDATION_DATE) values(: 2,:3,: 4,:5,: 6,:7,: 8)'
                    cur.execute(statement, (
                     ATT_DATE,ATT_TIME, CARD_NO, CREATION_DATE, MAC_NUMBER,REMARKS,UPDATION_DATE))
                    conn.commit()
                    wfh.update({
                       'wfh_posted': True
                    })


    def _action_re_send_wfh_attendance_data(self):
        unreconcile_wfh = self.env['hr.attendance'].search([('wfh_posted','=',True),('remarks','=','WFH(Work From Home)')])     
        for wfh in unreconcile_wfh:
            if wfh.remarks == 'WFH(Work From Home)' and wfh.wfh_posted==True:
                if wfh.check_in:
                    ATT_DATE = str(wfh.att_date)
                    if wfh.att_date: 
                        ATT_DATE = str(wfh.att_date.strftime('%m/%d/%Y'))
                    att_time = wfh.check_in + relativedelta(hours =+ 5) 
                    ATT_TIME = att_time.strftime('%H%M%S')
                    CARD_NO = wfh.employee_id.barcode
                    CREATION_DATE = wfh.check_in + relativedelta(hours =+ 5)
                    MAC_NUMBER = 48
                    REMARKS = wfh.remarks
                    UPDATION_DATE = fields.datetime.today()
                    conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                    cur = conn.cursor()
                    existing_statement='select ATT_DATE,ATT_TIME, CARD_NO, CREATION_DATE, MAC_NUMBER,REMARKS,UPDATION_DATE from ODOO_ATTEND_DATA'
                    cur.execute(existing_statement)
                    existing_wfh= cur.fetchall()
                    ora_unposted=False
                    for exist_wfh in existing_wfh:
                        if  exist_wfh[2]==CARD_NO and exist_wfh[0]==ATT_DATE and exist_wfh[1]==ATT_TIME: 
                            pass
                        else:
                            ora_unposted=True
                    if ora_unposted==True:
                        statement = 'insert into ODOO_ATTEND_DATA(ATT_DATE,ATT_TIME, CARD_NO, CREATION_DATE, MAC_NUMBER,REMARKS,UPDATION_DATE) values(: 2,:3,: 4,:5,: 6,:7,: 8)'
                        cur.execute(statement, (
                        ATT_DATE,ATT_TIME, CARD_NO, CREATION_DATE, MAC_NUMBER,REMARKS,UPDATION_DATE))
                        conn.commit()
                        wfh.update({
                        'wfh_posted': True
                        })
      
                if wfh.check_out:
                    ATT_DATE = str(wfh.att_date)
                    if wfh.att_date:  
                        ATT_DATE = str(wfh.att_date.strftime('%m/%d/%Y'))
                    out_time = wfh.check_out + relativedelta(hours =+ 5)
                    ATT_TIME = out_time.strftime('%H%M%S')
                    CARD_NO = wfh.employee_id.barcode
                    CREATION_DATE = wfh.check_out + relativedelta(hours =+ 5)
                    MAC_NUMBER = 49
                    REMARKS = wfh.remarks
                    UPDATION_DATE = fields.datetime.today()
                    conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                    cur = conn.cursor()
                    existing_statement='select ATT_DATE,ATT_TIME, CARD_NO, CREATION_DATE, MAC_NUMBER,REMARKS,UPDATION_DATE from ODOO_ATTEND_DATA'
                    cur.execute(existing_statement)
                    out_exist_wfh= cur.fetchall()
                    outtime_ora_unposted=False
                    for out_exist_wfh in out_exist_wfh:
                        if  out_exist_wfh[2]==CARD_NO and out_exist_wfh[0]==ATT_DATE and out_exist_wfh[1]==ATT_TIME: 
                            pass
                        else:
                            outtime_ora_unposted=True
                    if outtime_ora_unposted==True:
                        statement = 'insert into ODOO_ATTEND_DATA(ATT_DATE,ATT_TIME, CARD_NO, CREATION_DATE, MAC_NUMBER,REMARKS,UPDATION_DATE) values(: 2,:3,: 4,:5,: 6,:7,: 8)'
                        cur.execute(statement, (
                        ATT_DATE,ATT_TIME, CARD_NO, CREATION_DATE, MAC_NUMBER,REMARKS,UPDATION_DATE))
                        conn.commit()
                        wfh.update({
                        'wfh_posted': True
                        })