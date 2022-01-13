# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ControlledAccount(models.Model):
    _name = 'controlled.account'
    _description = 'Controlled Account'
    
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    
    
    