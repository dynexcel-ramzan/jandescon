# -*- coding: utf-8 -*-

from odoo import api, models, modules,fields, _
from odoo.exceptions import UserError


class hrContractInherit(models.Model):
    _inherit = 'hr.contract'
    name = fields.Char(required=True)
    
    @api.model
    def create(self, vals):
        sql = """ select name from hr_contract where name ='""" + vals['name'] + """' """
        self.env.cr.execute(sql)
        st = self.env.cr.fetchone()
#         raise UserError((type(st[0])))
        if st:
            if str(st[0]) == str(vals['name']):
                raise UserError(('Contract Reference already exits! '))
        res = super(hrContractInherit, self).create(vals)
        return res

            
        
        
        