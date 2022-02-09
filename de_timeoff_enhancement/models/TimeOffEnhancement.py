from odoo import models, fields, api


class HRTimeOff(models.Model):
    _inherit = 'hr.leave.type'

    target_year = fields.Selection([('2020', '2020'), ('2021', '2021'),('2022', '2022'), ('2023', '2023')
                                    ,('2024', '2024'), ('2025', '2025'),('2026', '2026'), ('2027', '2027')
                                    ,('2028', '2028'), ('2029', '2029'),('2030', '2031'), ('2032', '2032')
                                    ,('2033', '2033'), ('2034', '2034'),('2035', '2035'), ('2036', '2036')
                                    ,('2037', '2037'), ('2038', '2038'),('2039', '2039'), ('2040', '2040')],string="Target Year")
    allow_carry_over = fields.Boolean( string = "Allow Carry Over" )
    max_balance_after_carry_over = fields.Integer( string="Max Balance After Carry Over (In Days) ")
    is_annual_leave = fields.Boolean(string= "Annual Leaves ")