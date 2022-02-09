from odoo import models, fields, api, _

class FiscalYear(models.Model):
    _name = 'fiscal.year'
    _description = 'Fiscal Year'

    name = fields.Char(string='Name')

