# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    chanceller_id = fields.Many2one('hr.employee', string='Vice-Chairman')
    finance_partner_id = fields.Many2one('hr.employee', string='FBP')
    is_fbp_approval = fields.Boolean(string='FBP Approval')
    

