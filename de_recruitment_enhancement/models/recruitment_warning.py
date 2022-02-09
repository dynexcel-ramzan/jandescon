
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WarningWizard(models.TransientModel):
    _name = 'warning.wizard'

    warning = fields.Char()

    def create_next_date(self):
        pass