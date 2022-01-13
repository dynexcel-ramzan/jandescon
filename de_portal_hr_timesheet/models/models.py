# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class portal_hr_timesheet(models.Model):
    _inherit = 'account.analytic.line'

    
    
    
class project_project(models.Model):
    _inherit = 'project.project'
    
class project_task(models.Model):
    _inherit = 'project.task'    