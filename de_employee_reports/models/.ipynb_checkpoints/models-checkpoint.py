# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ORAFiscalYear(models.Model):
    _name = 'ora.fiscal.year'
    _description = 'ORA Fiscal Year'

    name = fields.Char(string='Name')
