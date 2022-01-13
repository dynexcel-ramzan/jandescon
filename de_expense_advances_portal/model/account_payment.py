# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

    

class AccountPayment(models.Model):
    _inherit = 'account.payment'  
    
    
class HrEmployee(models.Model):
    _inherit = 'hr.employee'  
    
    
class ResUser(models.Model):
    _inherit = 'res.users'  
    
    
class ResPartner(models.Model):
    _inherit = 'res.partner'  
    