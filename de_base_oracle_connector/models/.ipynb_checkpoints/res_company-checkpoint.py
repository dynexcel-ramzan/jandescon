# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
from odoo.exceptions import ValidationError


logger = logging.getLogger(__name__)




class ResCompany(models.Model):
    _inherit = 'res.company'

    ledger_id = fields.Integer(string="Ledger ID")
    segment1 = fields.Integer(string="Company Code")
    



















