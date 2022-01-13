from odoo import api, fields, models, _

class ProductProduct(models.Model):
    _inherit = 'product.product'

    # can_be_expense = fields.Boolean(string="can be Expense", related = 'holiday_status_id.')
    is_petty_cash = fields.Boolean(string='Is Petty Cash', default=False)