# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
import cx_Oracle


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    oralce_employee_no = fields.Char(string="EBS Employee No.")


    def action_fetch_oracle_attendance(self):
        conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
        cur = conn.cursor()
        for employee in self:
            statement = '''select p.att_time AS timestamp, p.mac_number AS machine, p.card_no AS card, p.att_date AS attendance_date, p.creation_date AS creation_date, p.remarks AS remarks, p.updation_date AS updation_date from attend_data p where p.creation_date>=sysdate-35 and p.card_no='''+str(employee.barcode)+''''''
            cur.execute(statement)
            attendances = cur.fetchall()  
            for attendance in attendances:
                ebs_timestamp1 = attendance[6].strftime("%Y-%m-%d %H:%M:%S")
                ebs_timestamp = datetime.strptime(ebs_timestamp1, '%Y-%m-%d %H:%M:%S') - relativedelta(hours =+ 5)
                ebs_attendance_data1 =  ebs_timestamp.strftime('%Y-%m-%d')
                ebs_attendance_data = datetime.strptime(ebs_attendance_data1, '%Y-%m-%d')
                duplicate_attendance = user_attendance.search([('card_no','=',attendance[2]),('time','=',attendance[0]),('attendance_date','=',ebs_attendance_data)], limit=1)
                if not duplicate_attendance:
                    employee = self.env['hr.employee'].search([('barcode','=',attendance[2])], limit=1)
                    timestamdata = attendance[6]
                    timestamp1 = timestamdata.strftime("%Y-%m-%d %H:%M:%S")
                    timestamp = datetime.strptime(timestamp1, '%Y-%m-%d %H:%M:%S') - relativedelta(hours =+ 5)
                    attendance_data1 =  attendance[3]
                    attendance_data = datetime.strptime(timestamp1, '%Y-%m-%d %H:%M:%S')
                    timedata = attendance[0]
                    time = timedata
                    vals = {
                     'timestamp': timestamp,
                     'device_id': attendance[1],
                     'employee_id': employee.id,
                     'card_no': attendance[2],
                     'attendance_date': attendance_data,
                     'creation_date': attendance[4],
                     'company_id': employee.company_id.id,
                     'remarks': attendance[5],
                     'time':  attendance[0],
                     'updation_date': attendance[6],
                    }
                    user_attendance= self.env['hr.user.attendance'].create(vals)
                    in_attendance_exist = self.env['hr.employee'].search([('employee_id','=',employee.id),('att_date','=',ebs_attendance_data),('check_in','<=',timestamp)], limit=1)
                    out_attendance_exist = self.env['hr.employee'].search([('employee_id','=',employee.id),('att_date','=',ebs_attendance_data),('check_out','>=',timestamp)], limit=1)
                    if in_attendance_exist:
                        in_attendance_exist.update({
                           'check_out': timestamp,
                        })
                    elif out_attendance_exist:
                        in_attendance_exist.update({
                           'check_in': timestamp,
                        })
                    else:
                        att_vals = {
                            'employee_id': employee.id,  
                            'check_in': timestamp,
                            'att_date': timestamp, 
                        }
                        attendance_vals = self.env['hr.attendance'].sudo().create(att_vals)
