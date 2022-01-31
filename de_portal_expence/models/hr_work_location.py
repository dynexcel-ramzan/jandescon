# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class WorkLocation(models.Model):
    _inherit = 'hr.work.location'
    
    approver_id = fields.Many2one('hr.employee', string='Approver')
    
    