# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date
from random import randint


class HrLoanType(models.Model):
    _inherit = 'hr.loan.type'
 
    
    def _get_default_color(self):
        return randint(1, 11)
    
    category_id = fields.Many2one('approval.category', string="Category", required=False)
    color = fields.Integer(string='Color', default=_get_default_color)

   
