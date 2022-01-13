from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    can_request_petty_cash = fields.Boolean('Can Request Petty Cash')
    petty_cash_limit = fields.Integer(string='Petty Cash Limit', required=True)
    petty_cash_period = fields.Selection([('1', '1 Year'), ('2', '2 Year'), ('3', '3 Year'), ('4', '4 Year')]
                                            , string='Petty Cash Period')
    can_request_funds_expense = fields.Boolean('Can Request Funds for Expense')

    @api.onchange('petty_cash_limit')
    def onchnage_petty_cash_limit(self):
        if self.petty_cash_limit > 1000000:
            raise UserError("Petty Cash Limit Cannot be Greater Than 1000000(1M)")

    @api.onchange('can_request_petty_cash')
    def onchange_can_request_petty_cash(self):
        if self.can_request_petty_cash == False:
            self.petty_cash_limit = 0
            self.petty_cash_period = False
