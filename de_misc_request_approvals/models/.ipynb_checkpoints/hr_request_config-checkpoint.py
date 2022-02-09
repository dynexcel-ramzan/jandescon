# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrRequestConf(models.Model):
    _inherit = 'hr.request.config'
    
    approval_category_id = fields.Many2one('approval.category', string="Category", required=False)
   
 