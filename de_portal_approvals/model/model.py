# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    
class ApprovalCategory(models.Model):
    _inherit = 'approval.category'    
    
    
    
class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    
    def  action_date_confirm_update(self):
        for line in self:
            date_confirm = fields.datetime.now() + timedelta(60)
            line.update({
               'date_confirmed': date_confirm
            })
            mail = self.env['mail.activity'].search([('res_id','=',line.id)])
            date_dead = fields.date.today() + timedelta(60)
            mail.update ({
               'date_deadline': date_dead
              })
   
    def  action_date_confirm_update_reverse(self):
        for line in self:
            date_confirm = fields.datetime.now() - timedelta(1)
            line.update({
               'date_confirmed': date_confirm
            })
            mail = self.env['mail.activity'].search([('res_id','=',line.id)])
            date_dead = fields.date.today()  + timedelta(1)
            mail.update ({
               'date_deadline': date_dead
              })     

class ResUser(models.Model):
    _inherit = 'res.users'     
    
    
    
