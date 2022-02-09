# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
from odoo.exceptions import ValidationError


logger = logging.getLogger(__name__)




class AccountAccount(models.Model):
    _inherit = 'account.account'

    segment2 = fields.Integer(string="Segment 2")
    segment3 = fields.Integer(string="Segment 3")
    segment4 = fields.Integer(string="Segment 4")
    segment5 = fields.Integer(string="Segment 5")
    segment6 = fields.Integer(string="Segment 6")

















