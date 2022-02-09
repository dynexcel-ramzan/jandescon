# -*- coding: utf-8 -*-

from odoo import api, fields, models, _



class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    
class ApprovalCategory(models.Model):
    _inherit = 'approval.category'    
    
    
    
class ApprovalRequest(models.Model):
    _inherit = 'approval.request'   
    

class ResUser(models.Model):
    _inherit = 'res.users'     
    
    
    
