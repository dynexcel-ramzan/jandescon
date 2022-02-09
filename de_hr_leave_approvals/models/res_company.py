# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    manager_id = fields.Many2one('hr.employee',string='CEO')
    