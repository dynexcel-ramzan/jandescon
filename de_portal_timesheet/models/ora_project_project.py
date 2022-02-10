# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import cx_Oracle

class ORAProjectProject(models.Model):
    _inherit = 'project.project'

    
    ora_code = fields.Char(string='Code')
    ora_client_id = fields.Many2one('res.ora.client',string='Client')
    ora_category_id = fields.Many2one('res.ora.category',string='Category')
    ora_city=fields.Char(string='City')
    ora_region = fields.Char(string='Region')
    ora_enabled = fields.Boolean(string='Enabled')
    ora_job_duration = fields.Char(string='Job Duration')
    ora_close_date = fields.Date(string='Close Date')
    ora_mobilization_date = fields.Date(string='Start Date')
    ora_record_id = fields.Integer(string='Ora Record Id')
    ora_status = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('close', 'Closed')
         ],
        readonly=False, string='Status')

    def _action_fetch_oracle_project(self):
        conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//192.168.65.152:1523/test2')
        cur = conn.cursor()
        statement = "select p.id as id, p.code as code, p.descr as des, p.customer_name as cust_name, p.customer_number as cust_number, p.category as category, p.job_duration as job_duration, p.city as city, p.region as region, p.close_date as close_date, p.mobilization_date as end_date from XX_APPS_IPL_PROJECTS p where p.status='APPROVED' and p.enabled='Y' and p.customer_name is not null"
        cur.execute(statement)
        projects = cur.fetchall()
        for prj in projects:
            duplicate_rec = self.env['project.project'].search([('ora_record_id','=',prj[0])])
            if duplicate_rec:
                ora_clinet = self.env['res.ora.client'].search([('code','=',prj[4])])
                if not ora_clinet:
                    vals={
                        'name': prj[3],
                        'code': prj[4],
                    }
                    ora_clinet = self.env['res.ora.client'].create(vals)
                ora_category = self.env['res.ora.category'].search([('name', '=', prj[5])])
                if not ora_category:
                    categ_vals = {
                        'name': prj[5],
                    }
                    ora_category = self.env['res.ora.category'].create(categ_vals)
                duplicate_rec.update({
                  'name': str(prj[1] if prj[1] else ' ' ) +' ('+str(prj[2] if prj[2] else ' ' )+')' ,
                  'ora_code':  prj[1],
                  'ora_record_id': prj[0],
                  'ora_client_id': ora_clinet.id,
                  'ora_category_id': ora_category.id,
                  'ora_enabled': True,
                  'ora_job_duration': prj[6],
                  'ora_city': prj[7],
                  'ora_region': prj[8],
                  'ora_enabled': True, 
                  'ora_status': 'approved',
                  'ora_close_date': prj[9] if prj[9] else False, 
                  'ora_mobilization_date': prj[10] if prj[10] else False,     
                })
            if not duplicate_rec:
                ora_clinet = self.env['res.ora.client'].search([('code','=',prj[4])])
                if not ora_clinet:
                    vals={
                        'name': prj[3],
                        'code': prj[4],
                    }
                    ora_clinet = self.env['res.ora.client'].create(vals)
                ora_category = self.env['res.ora.category'].search([('name', '=', prj[5])])
                if not ora_category:
                    categ_vals = {
                        'name': prj[5],
                    }
                    ora_category = self.env['res.ora.category'].create(categ_vals)
                project_value = {
                    'name': str(prj[1] if prj[1] else ' ' ) +' ('+str(prj[2] if prj[2] else ' ' )+')' ,
                    'ora_code':  prj[1],
                    'ora_record_id': prj[0],
                    'ora_client_id': ora_clinet.id,
                    'ora_category_id': ora_category.id,
                    'ora_enabled': True,
                    'ora_job_duration': prj[6],
                    'ora_city': prj[7],
                    'ora_enabled': True,
                    'ora_status': 'approved',
                    'ora_region': prj[8],
                    'ora_close_date': prj[9] if prj[9] else False, 
                    'ora_mobilization_date': prj[10] if prj[10] else False,    
                }
                project = self.env['project.project'].sudo().create(project_value)

