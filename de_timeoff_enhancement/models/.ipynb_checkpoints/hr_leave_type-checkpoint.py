from odoo import models, fields, api


class HRTimeOff(models.Model):
    _inherit = 'hr.leave.type'

    fiscal_year_id = fields.Many2one('fiscal.year' , string='Target Year')
    allow_carry_over = fields.Boolean( string = "Allow Carry Over" )
    max_balance_after_carry_over = fields.Integer( string="Max Balance After Carry Over (In Days) ")
    is_annual_leave = fields.Boolean(string= "Annual Leaves ")