from odoo import models, fields, api


class HRTimeOff(models.Model):
    _inherit = 'hr.leave.type'

    fiscal_year = fields.Char(string='Target Year')
    allow_carry_over = fields.Boolean( string = "Allow Carry Over" )
    max_balance_after_carry_over = fields.Integer( string="Max Balance After Carry Over (In Days) ")
    is_annual_leave = fields.Boolean(string= "Annual Leaves ")

    @api.onchange('validity_start')
    def onchange_validity_start(self):
        for line in self:
            if line.validity_start:
                line.update({
                           'fiscal_year': line.validity_start.year, 
                           }) 