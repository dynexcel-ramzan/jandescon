# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    approver_ids = fields.Many2many('hr.employee', string='Approver')
    
   