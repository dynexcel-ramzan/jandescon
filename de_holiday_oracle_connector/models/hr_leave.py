# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import cx_Oracle
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta

class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    ebs_type_number = fields.Integer(string='EBS Number')  


class IrConfig(models.Model):
    _inherit = 'ir.config_parameter'

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    
    leave_period_half = fields.Selection([
        ('first_half', 'First Half'),
        ('second_half', 'Second Half'),
        ], string='Half', tracking=True)

    short_start_time = fields.Float(string='Start Time')
    is_posted = fields.Boolean(string='Post to Oracle')

    def action_send_leave_data_fetch(self):
         
        conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')    
        cur = conn.cursor()
        statement = "select * from ODOO_LEAVE_TRANSACTION"
        cur.execute(statement)
        comitment_data = cur.fetchall()
        astatement = "select count(*) from ODOO_LEAVE_TRANSACTION"
        cur.execute(astatement)
        acomitment_data = cur.fetchall()        
        raise UserError('Count('+str(acomitment_data)+')  '+str(comitment_data))   
 
    def action_re_send_holiday_data(self):
        holidays = self.env['hr.leave'].search([('is_posted','=', True),('state','=','validate'),('request_date_from','>','2021-07-15'),('holiday_status_id.name','!=','Rest Day')], limit=100)
        
        for leave in self:
            if leave.is_posted == True and leave.state =='validate':
                conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                cur = conn.cursor()
                statement = """select * from ODOO_LEAVE_TRANSACTION where REMARKS=""" + str(leave.id) + """ """
                cur.execute(statement)
                already_exist_data = cur.fetchall()
                if already_exist_data:
                    pass
                else: 
                    if leave.employee_id.barcode and leave.employee_id.parent_id.barcode:
                        ACTIVITY_ID = 2
                        CREATED_BY = leave.employee_id.barcode.lstrip("0")
                        OFFICE_EMP_ID = leave.employee_id.barcode.lstrip("0")
                        APPROVED_BY = leave.employee_id.parent_id.barcode.lstrip("0")
                        FORWARDED_TO =  leave.employee_id.parent_id.barcode.lstrip("0")
                        APPROVED_DATE = leave.approve_date if leave.approve_date else leave.request_date_from
                        COMPANY_ID = leave.employee_id.company_id.segment1
                        CREATION_DATE = leave.create_date
                        EFFECTIVE_DATE = leave.request_date_from
                        EMPLOYEE_ID = leave.employee_id.barcode.lstrip("0")
                        END_DATE = leave.request_date_to
                        LEAVE_DAYS = -leave.number_of_days
                        LEAVE_DAY_TYPE = 'Full Day'
                        LEAVE_DAY_TYPE = leave.leave_category
                        if leave.leave_category == 'day':
                            LEAVE_DAY_TYPE = 'Full Day'
                        if leave.leave_category == 'half_day':
                            if leave.leave_period_half == 'first_half':
                                LEAVE_DAY_TYPE = 'First Half'
                            if leave.leave_period_half == 'second_half':
                                LEAVE_DAY_TYPE = 'Second Half'
                        if leave.leave_category == 'hours':
                            LEAVE_DAY_TYPE = 'Short Leave'
                        LEAVE_STATUS = ' '
                        if leave.state == 'validate':
                            LEAVE_STATUS = 'A'
                        LEAVE_TYPE_ID = leave.holiday_status_id.ebs_type_number
                        REASON = leave.name if leave.name else ' '
                        REMARKS = leave.id
                        START_DATE = leave.request_date_from

                        TRANSACTION_ID = leave.id
                        YEAR = fields.date.today().year
                        if leave.number_of_days > 3 and leave.holiday_status_id.ebs_type_number ==2:
                            HR_ACTION_DATE =  leave.request_date_from + timedelta(1)
                            HR_APPROVAL_FLG = 1
                            if leave.employee_id.company_id.hr_id:
                                HR_APPROVAL_ID = leave.employee_id.company_id.hr_id.barcode.lstrip("0")
                                HR_APPROVAL_REQUIRED = 'Y'
                                conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                                cur = conn.cursor()
                                statement = 'insert into ODOO_LEAVE_TRANSACTION(ACTIVITY_ID,OFFICE_EMP_ID,APPROVED_BY, APPROVED_DATE, COMPANY_ID,CREATED_BY,CREATION_DATE,EFFECTIVE_DATE,EMPLOYEE_ID,END_DATE,  FORWARDED_TO, HR_ACTION_DATE, HR_APPROVAL_FLG, HR_APPROVAL_ID, HR_APPROVAL_REQUIRED, LEAVE_DAYS, LEAVE_DAY_TYPE, LEAVE_STATUS, LEAVE_TYPE_ID, REASON, REMARKS, START_DATE, TRANSACTION_ID,YEAR) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,: 14,:15,: 16,:17,: 18,:19,: 20,:21,: 22,:23,:24,:25)'
                                cur.execute(statement, (
                                 ACTIVITY_ID,OFFICE_EMP_ID,APPROVED_BY, APPROVED_DATE, COMPANY_ID,CREATED_BY,CREATION_DATE,EFFECTIVE_DATE,EMPLOYEE_ID,END_DATE,  FORWARDED_TO, HR_ACTION_DATE, HR_APPROVAL_FLG, HR_APPROVAL_ID, HR_APPROVAL_REQUIRED, LEAVE_DAYS, LEAVE_DAY_TYPE, LEAVE_STATUS, LEAVE_TYPE_ID, REASON, REMARKS, START_DATE, TRANSACTION_ID,YEAR))
                                conn.commit()
                                leave.update({
                                    'is_posted': True
                                })
                        elif leave.leave_category == 'hours':
                            START_TIME = leave.date_from  + relativedelta(hours =+ 5)
                            END_TIME  = leave.date_to + relativedelta(hours =+ 5)
                            conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                            cur = conn.cursor()
                            statement = 'insert into ODOO_LEAVE_TRANSACTION(START_TIME, END_TIME, ACTIVITY_ID,OFFICE_EMP_ID,APPROVED_BY, APPROVED_DATE, COMPANY_ID,CREATED_BY,CREATION_DATE,EFFECTIVE_DATE,EMPLOYEE_ID,END_DATE,  FORWARDED_TO,LEAVE_DAYS, LEAVE_DAY_TYPE, LEAVE_STATUS, LEAVE_TYPE_ID, REASON, REMARKS, START_DATE, TRANSACTION_ID,YEAR) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,: 14,:15,: 16,:17,: 18,:19,: 20,:21,: 22,:23)'
                            cur.execute(statement, (
                             START_TIME, END_TIME, ACTIVITY_ID,OFFICE_EMP_ID,APPROVED_BY, APPROVED_DATE, COMPANY_ID,CREATED_BY,CREATION_DATE,EFFECTIVE_DATE,EMPLOYEE_ID,END_DATE,  FORWARDED_TO, LEAVE_DAYS, LEAVE_DAY_TYPE, LEAVE_STATUS, LEAVE_TYPE_ID, REASON, REMARKS, START_DATE, TRANSACTION_ID,YEAR))
                            conn.commit()
                            leave.update({
                                'is_posted': True
                                })
                        else:
                            conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                            cur = conn.cursor()
                            statement = 'insert into ODOO_LEAVE_TRANSACTION(ACTIVITY_ID,OFFICE_EMP_ID,APPROVED_BY, APPROVED_DATE, COMPANY_ID,CREATED_BY,CREATION_DATE,EFFECTIVE_DATE,EMPLOYEE_ID,END_DATE,  FORWARDED_TO,LEAVE_DAYS, LEAVE_DAY_TYPE, LEAVE_STATUS, LEAVE_TYPE_ID, REASON, REMARKS, START_DATE, TRANSACTION_ID,YEAR) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,: 14,:15,: 16,:17,: 18,:19,: 20,:21)'
                            cur.execute(statement, (
                            ACTIVITY_ID,OFFICE_EMP_ID,APPROVED_BY, APPROVED_DATE, COMPANY_ID,CREATED_BY,CREATION_DATE,EFFECTIVE_DATE,EMPLOYEE_ID,END_DATE,  FORWARDED_TO, LEAVE_DAYS, LEAVE_DAY_TYPE, LEAVE_STATUS, LEAVE_TYPE_ID, REASON, REMARKS, START_DATE, TRANSACTION_ID,YEAR))
                            conn.commit()
                            leave.update({
                                'is_posted': True
                                })

                        leave.action_send_holiday_line_data(leave.id)
                        leave.update({
                            'is_posted' : True
                             })


    def action_send_holiday_data(self):
        holidays = self.env['hr.leave'].search([('is_posted','!=', True),('state','=','validate'),('request_date_from','>','2021-07-15'),('holiday_status_id.name','!=','Rest Day')], limit=100)
        
        for leave in holidays:
            if leave.is_posted == False and leave.state =='validate': 
                if leave.employee_id.barcode and leave.employee_id.parent_id.barcode:
                    ACTIVITY_ID = 2
                    CREATED_BY = leave.employee_id.barcode.lstrip("0")
                    OFFICE_EMP_ID = leave.employee_id.barcode.lstrip("0")
                    APPROVED_BY = leave.employee_id.parent_id.barcode.lstrip("0")
                    FORWARDED_TO =  leave.employee_id.parent_id.barcode.lstrip("0")
                    APPROVED_DATE = leave.approve_date if leave.approve_date else leave.request_date_from
                    COMPANY_ID = leave.employee_id.company_id.segment1
                    CREATION_DATE = leave.create_date
                    EFFECTIVE_DATE = leave.request_date_from
                    EMPLOYEE_ID = leave.employee_id.barcode.lstrip("0")
                    END_DATE = leave.request_date_to
                    LEAVE_DAYS = -leave.number_of_days
                    LEAVE_DAY_TYPE = 'Full Day'
                    LEAVE_DAY_TYPE = leave.leave_category
                    if leave.leave_category == 'day':
                        LEAVE_DAY_TYPE = 'Full Day'
                    if leave.leave_category == 'half_day':
                        if leave.leave_period_half == 'first_half':
                            LEAVE_DAY_TYPE = 'First Half'
                        if leave.leave_period_half == 'second_half':
                            LEAVE_DAY_TYPE = 'Second Half'
                    if leave.leave_category == 'hours':
                        LEAVE_DAY_TYPE = 'Short Leave'
                    LEAVE_STATUS = ' '
                    if leave.state == 'validate':
                        LEAVE_STATUS = 'A'
                    LEAVE_TYPE_ID = leave.holiday_status_id.ebs_type_number
                    REASON = leave.name if leave.name else ' '
                    REMARKS = leave.id
                    START_DATE = leave.request_date_from

                    TRANSACTION_ID = leave.id
                    YEAR = fields.date.today().year
                    if leave.number_of_days > 3 and leave.holiday_status_id.ebs_type_number ==2:
                        HR_ACTION_DATE =  leave.request_date_from + timedelta(1)
                        HR_APPROVAL_FLG = 1
                        if leave.employee_id.company_id.hr_id:
                            HR_APPROVAL_ID = leave.employee_id.company_id.hr_id.barcode.lstrip("0")
                            HR_APPROVAL_REQUIRED = 'Y'
                            conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                            cur = conn.cursor()
                            statement = 'insert into ODOO_LEAVE_TRANSACTION(ACTIVITY_ID,OFFICE_EMP_ID,APPROVED_BY, APPROVED_DATE, COMPANY_ID,CREATED_BY,CREATION_DATE,EFFECTIVE_DATE,EMPLOYEE_ID,END_DATE,  FORWARDED_TO, HR_ACTION_DATE, HR_APPROVAL_FLG, HR_APPROVAL_ID, HR_APPROVAL_REQUIRED, LEAVE_DAYS, LEAVE_DAY_TYPE, LEAVE_STATUS, LEAVE_TYPE_ID, REASON, REMARKS, START_DATE, TRANSACTION_ID,YEAR) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,: 14,:15,: 16,:17,: 18,:19,: 20,:21,: 22,:23,:24,:25)'
                            cur.execute(statement, (
                             ACTIVITY_ID,OFFICE_EMP_ID,APPROVED_BY, APPROVED_DATE, COMPANY_ID,CREATED_BY,CREATION_DATE,EFFECTIVE_DATE,EMPLOYEE_ID,END_DATE,  FORWARDED_TO, HR_ACTION_DATE, HR_APPROVAL_FLG, HR_APPROVAL_ID, HR_APPROVAL_REQUIRED, LEAVE_DAYS, LEAVE_DAY_TYPE, LEAVE_STATUS, LEAVE_TYPE_ID, REASON, REMARKS, START_DATE, TRANSACTION_ID,YEAR))
                            conn.commit()
                            leave.update({
                                'is_posted': True
                            })
                    elif leave.leave_category == 'hours':
                        START_TIME = leave.date_from  + relativedelta(hours =+ 5)
                        END_TIME  = leave.date_to + relativedelta(hours =+ 5)
                        conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                        cur = conn.cursor()
                        statement = 'insert into ODOO_LEAVE_TRANSACTION(START_TIME, END_TIME, ACTIVITY_ID,OFFICE_EMP_ID,APPROVED_BY, APPROVED_DATE, COMPANY_ID,CREATED_BY,CREATION_DATE,EFFECTIVE_DATE,EMPLOYEE_ID,END_DATE,  FORWARDED_TO,LEAVE_DAYS, LEAVE_DAY_TYPE, LEAVE_STATUS, LEAVE_TYPE_ID, REASON, REMARKS, START_DATE, TRANSACTION_ID,YEAR) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,: 14,:15,: 16,:17,: 18,:19,: 20,:21,: 22,:23)'
                        cur.execute(statement, (
                         START_TIME, END_TIME, ACTIVITY_ID,OFFICE_EMP_ID,APPROVED_BY, APPROVED_DATE, COMPANY_ID,CREATED_BY,CREATION_DATE,EFFECTIVE_DATE,EMPLOYEE_ID,END_DATE,  FORWARDED_TO, LEAVE_DAYS, LEAVE_DAY_TYPE, LEAVE_STATUS, LEAVE_TYPE_ID, REASON, REMARKS, START_DATE, TRANSACTION_ID,YEAR))
                        conn.commit()
                        leave.update({
                            'is_posted': True
                            })
                    else:
                        conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                        cur = conn.cursor()
                        statement = 'insert into ODOO_LEAVE_TRANSACTION(ACTIVITY_ID,OFFICE_EMP_ID,APPROVED_BY, APPROVED_DATE, COMPANY_ID,CREATED_BY,CREATION_DATE,EFFECTIVE_DATE,EMPLOYEE_ID,END_DATE,  FORWARDED_TO,LEAVE_DAYS, LEAVE_DAY_TYPE, LEAVE_STATUS, LEAVE_TYPE_ID, REASON, REMARKS, START_DATE, TRANSACTION_ID,YEAR) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9,: 10,:11,: 12,:13,: 14,:15,: 16,:17,: 18,:19,: 20,:21)'
                        cur.execute(statement, (
                        ACTIVITY_ID,OFFICE_EMP_ID,APPROVED_BY, APPROVED_DATE, COMPANY_ID,CREATED_BY,CREATION_DATE,EFFECTIVE_DATE,EMPLOYEE_ID,END_DATE,  FORWARDED_TO, LEAVE_DAYS, LEAVE_DAY_TYPE, LEAVE_STATUS, LEAVE_TYPE_ID, REASON, REMARKS, START_DATE, TRANSACTION_ID,YEAR))
                        conn.commit()
                        leave.update({
                            'is_posted': True
                            })

                    leave.action_send_holiday_line_data(leave.id)
                    


    def action_send_holiday_line_data(self,leave):
        leaves = self.env['hr.leave'].search([('id','=',leave)]) 
        for leave in leaves:
            if leave.number_of_days >=  1:            
                for day in range(round(leave.number_of_days)):            
                    EMPLOYEE_ID = leave.employee_id.barcode.lstrip("0")
                    ENABLED = 'Y'
                    LEAVE_DATE = leave.request_date_from + timedelta(day)
                    LEAVE_DAYS = -1
                    LEAVE_DAY_TYPE = 'Full Day'
                    if leave.leave_category == 'day':
                        LEAVE_DAY_TYPE = 'Full Day'  
                    if leave.leave_category == 'half_day':
                        if leave.leave_period_half == 'first_half':
                            LEAVE_DAY_TYPE = 'First Half'
                        if leave.leave_period_half == 'second_half':
                            LEAVE_DAY_TYPE = 'Second Half'
                    if leave.leave_category == 'hours':
                        LEAVE_DAY_TYPE = 'Short Leave'
                     
                    individual_id = str(leave.id) + str(day)             
                    LTD_ID = int(individual_id)
                    TRANSACTION_ID = leave.id
                    YEAR = fields.date.today().year            
                    conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                    cur = conn.cursor()
                    statement = 'insert into ODOO_LEAVE_TRANSACTION_DTL(EMPLOYEE_ID,ENABLED, LEAVE_DATE, LEAVE_DAYS,LEAVE_DAY_TYPE,LTD_ID,TRANSACTION_ID,YEAR) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9)'
                    cur.execute(statement, (
                    EMPLOYEE_ID,ENABLED, LEAVE_DATE, LEAVE_DAYS,LEAVE_DAY_TYPE,LTD_ID,TRANSACTION_ID,YEAR))
                    conn.commit()
            else:
                EMPLOYEE_ID = leave.employee_id.barcode.lstrip("0")
                ENABLED = 'Y'
                LEAVE_DATE = leave.request_date_from
                LEAVE_DAYS = -0.5
                if leave.number_of_days == 0.25:
                    LEAVE_DAYS = -0.25
                LEAVE_DAY_TYPE = leave.leave_category
                if leave.leave_category == 'day':
                    LEAVE_DAY_TYPE = 'Full Day'  
                if leave.leave_category == 'half_day':
                    if leave.leave_period_half == 'first_half':
                        LEAVE_DAY_TYPE = 'First Half'
                    if leave.leave_period_half == 'second_half':
                        LEAVE_DAY_TYPE = 'Second Half'
                if leave.leave_category == 'hours':
                    LEAVE_DAY_TYPE = 'Short Leave'
                              
                individual_id = leave.id        
                LTD_ID = int(individual_id) 
                TRANSACTION_ID = leave.id
                YEAR = fields.date.today().year           
                conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
                cur = conn.cursor()
                statement = 'insert into ODOO_LEAVE_TRANSACTION_DTL(EMPLOYEE_ID,ENABLED, LEAVE_DATE, LEAVE_DAYS,LEAVE_DAY_TYPE,LTD_ID,TRANSACTION_ID,YEAR) values(: 2,:3,: 4,:5,: 6,:7,: 8,:9)'
                cur.execute(statement, (
                  EMPLOYEE_ID,ENABLED, LEAVE_DATE, LEAVE_DAYS,LEAVE_DAY_TYPE,LTD_ID,TRANSACTION_ID,YEAR))
                conn.commit()

