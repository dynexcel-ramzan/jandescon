# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VehicleMeterDetail(models.Model):
    _name = 'vehicle.meter.detail'
    _description = 'Vehicle Meter Detail'
    
    name = fields.Char(string='Name', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    company_id  = fields.Many2one('res.company', string='Company')
    grade_id = fields.Many2one('grade.designation', string='Designation')

