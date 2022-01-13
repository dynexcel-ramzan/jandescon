# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
from odoo.exceptions import ValidationError
import cx_Oracle

logger = logging.getLogger(__name__)



class OracleSettingConnector(models.Model):
    _name = 'oracle.setting.connector'
    _description = 'Oracle Database Instance'
    _order = "name desc"

    name = fields.Char(string='Instance Name', required=True)
    host = fields.Char(string="Host", required=True)
    port = fields.Char(string="Port", required=True)
    user = fields.Char(string="User Name", required=True)
    password = fields.Char(string="Password", required=True)
    db_name = fields.Char(string="Oracle Database", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('close', 'Close')],
        readonly=False, string='State', index=True , default='draft')

    def action_active(self):
        self.write({
            'state': 'active'
        })

    def try_connection(self):
        try:
            tusername = self.user
            tpasswrd = self.password
            thost = self.host
            tport = self.port
            tinstance = self.db_name
            conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.7.153:1524/test3')
            cur = conn.cursor()
            if conn:
                self.write({
                    'state': 'active'
                })
            if conn:
                raise ValidationError('Successfully Connected')



        except Exception as e:
            raise ValidationError(e)

    def action_get_attendance_data(self):
        attendance_ids = []
        conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.7.153:1524/test3')
        cur = conn.cursor()
        statement = 'select p.att_time AS timestamp, p.mac_number AS machine, p.card_no AS card, p.att_date AS attendance_date, p.creation_date AS creation_date, p.remarks AS remarks, p.updation_date AS updation_date from attend_data p'
        attendances = cur.execute(statement)
        for attendance in attendances:
            vals = {
                'timestamp': attendance['timestamp'],
                'mac_number': attendance['machine'],
                'card_no': attendance['card'],
                'att_date': attendance['attendance_date'],
                'creation_date': attendance['creation_date'],
                'remarks': attendance['remarks'],
                'updation_date': attendance['updation_date'],
            }
            user_attendance= self.env['hr.user.attendance'].create(vals)
            
        









