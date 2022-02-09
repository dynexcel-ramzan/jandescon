from odoo import api, fields, models, _


class CompanyInherited(models.Model):
    _inherit = "res.company"

    retirement_age = fields.Integer(string="Retirement Age")
