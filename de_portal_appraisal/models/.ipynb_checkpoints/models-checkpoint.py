# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PortalAppraisal(models.Model):
    _inherit = 'hr.appraisal.feedback'
    

class ResCompany(models.Model):
    _inherit = 'res.company'  
    
class HrAppraisalImprovements(models.Model):
    _inherit = 'hr.appraisal.improvements'  
    
class HrAppraisalImprovLine(models.Model):
    _inherit = 'hr.appraisal.improvements.line'     
    
class HrEmployee(models.Model):
    _inherit = 'hr.employee'      
    
class HrDepartment(models.Model):
    _inherit = 'hr.department'        
    

    
class AppraisalObjective(models.Model):
    _inherit = 'hr.appraisal.objective'    
    

class GradeType(models.Model):
    _inherit = 'grade.type'        
    
class HrAppraisalProbation(models.Model):
    _inherit = 'hr.appraisal.probation'          
    

class HrAppraisalObjectiveLine(models.Model):
    _inherit = 'hr.appraisal.objective.line'       
    
class HrAppraisalFeedbackAppraisee(models.Model):
    _inherit = 'hr.appraisal.feedback.values.appraisee.line'           
    
    
class HrAppraisalFeedbackobjAppraisee(models.Model):
    _inherit = 'hr.appraisal.feedback.objective.appraisee.line'               
    
    
class HrAppraisalFeedbackendyaerAppraisee(models.Model):
    _inherit = 'hr.appraisal.feedback.values.line'                   
    
    
class HrAppraisalFeedbackendyaer(models.Model):
    _inherit = 'hr.appraisal.feedback.objective.line'                       