# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class hr_expense(models.Model):
    _inherit = 'hr.expense'
    
    
    def action_draft(self):
        self.update({
            'state': 'draft'
        })
        self.sheet_id.reset_expense_sheets()
    
class ProductTemplate(models.Model):
    _inherit = 'product.template'         

    
class UomUom(models.Model):
    _inherit = 'uom.uom'         
        
    
class hr_employee_public(models.Model):
    _inherit = 'hr.employee.public' 
    

class ProductProduct(models.Model):
    _inherit = 'product.product'    
    
class GradeDesignationline(models.Model):
    _inherit = 'grade.designation.line'     

  
class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'     
    
class MailActivityType(models.Model):
    _inherit = 'mail.activity.type'     
           
    
class MailActivity(models.Model):
    _inherit = 'mail.activity'     