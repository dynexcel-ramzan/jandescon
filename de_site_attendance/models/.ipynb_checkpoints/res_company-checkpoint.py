from odoo import api, fields, models, _
from calendar import monthrange

from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    from_date = fields.Integer('Period From')
    to_date = fields.Integer('Period To')
    
    @api.onchange('from_date')
    def onchange_from_date(self):
        if self.from_date > 31:
            raise UserError('Not Allow To Enter grater than 31')
        if self.from_date < 0:
            raise UserError('Not Allow To Enter grater than 0')    
    
    
    @api.onchange('to_date')
    def onchange_to_date(self):
        if self.to_date > 31:
            raise UserError('Not Allow To Enter grater than 31')
        if self.to_date < 0:
            raise UserError('Not Allow To Enter grater than 0')    
    
    