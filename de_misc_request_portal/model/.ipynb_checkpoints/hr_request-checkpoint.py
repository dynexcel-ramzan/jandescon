# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

    

class HrRequestInh(models.Model):
    _inherit = 'hr.request'   
    
    

    
class HrRequestConfInh(models.Model):
    _inherit = 'hr.request.config' 
    
    