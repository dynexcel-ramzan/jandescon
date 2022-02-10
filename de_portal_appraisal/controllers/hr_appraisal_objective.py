# -*- coding: utf-8 -*-
from . import config
from . import update
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError
from collections import OrderedDict
from operator import itemgetter
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR
import ast
appraisal_objective_list = []
halfyear_objective_list = []

def appraisal_page_content(flag = 0):
    global appraisal_objective_list 
    managers = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    employees = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
    company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    categories = request.env['hr.objective.category'].search([])
    status = request.env['hr.objective.status'].search([])
    return {
        'managers': managers,
        'employees' : employees,
        'employee_name': employees,
        'managers': employees.parent_id.name,
        'categories': categories,
        'status': status,
        'appraisal_objective_list': appraisal_objective_list,
        'success_flag' : flag,
        'company_info': company_info,
    }

def appraisal_page_content_edit(editid):
    global appraisal_objective_list 
    managers = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    employees = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
    company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    categories = request.env['hr.objective.category'].search([])
    status = request.env['hr.objective.status'].search([])
    exist_line_obj = request.env['hr.appraisal.objective.line'].sudo().search([('id','=',editid)])
    return {
        'managers': managers,
        'employees' : employees,
        'exist_line_obj': exist_line_obj,
        'employee_name': employees,
        'managers': employees.parent_id.name,
        'categories': categories,
        'status': status,
        'appraisal_objective_list': appraisal_objective_list,
        'company_info': company_info,
    }

def appraisal_feedback_page_content_edit(editid,manager_edit, user_edit):
    global appraisal_objective_list 
    managers = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    employees = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
    company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    exist_line_obj = request.env['hr.appraisal.feedback.objective.appraisee.line'].sudo().search([('id','=',editid)])
    return {
        'managers': managers,
        'employees' : employees,
        'exist_line_obj': exist_line_obj,
        'employee_name': employees,
        'manager_edit': manager_edit,
        'user_edit': user_edit,
        'managers': employees.parent_id.name,
        'appraisal_objective_list': appraisal_objective_list,
        'company_info': company_info,
    }


def appraisal_full_year_obj_page_content_edit(editid,manager_edit, user_edit):
    managers = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    employees = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
    company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    exist_line_obj = request.env['hr.appraisal.feedback.objective.line'].sudo().search([('id','=',editid)])
    return {
        'managers': managers,
        'employees' : employees,
        'exist_line_obj': exist_line_obj,
        'employee_name': employees,
        'manager_edit': manager_edit,
        'user_edit': user_edit,
        'managers': employees.parent_id.name,
        'company_info': company_info,
    }


def appraisal_feedback_values_page_content_edit(editid,manager_edit, user_edit):
    global appraisal_objective_list 
    managers = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    employees = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
    company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    exist_line_obj = request.env['hr.appraisal.feedback.values.appraisee.line'].sudo().search([('id','=',editid)])
    return {
        'managers': managers,
        'employees' : employees,
        'exist_line_obj': exist_line_obj,
        'employee_name': employees,
        'manager_edit': manager_edit,
        'user_edit': user_edit,
        'managers': employees.parent_id.name,
        'appraisal_objective_list': appraisal_objective_list,
        'company_info': company_info,
    }


def appraisal_full_year_values_page_content_edit(editid,manager_edit, user_edit):
    global appraisal_objective_list 
    managers = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    employees = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
    company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    exist_line_obj = request.env['hr.appraisal.feedback.values.line'].sudo().search([('id','=',editid)])
    return {
        'managers': managers,
        'employees' : employees,
        'exist_line_obj': exist_line_obj,
        'employee_name': employees,
        'manager_edit': manager_edit,
        'user_edit': user_edit,
        'managers': employees.parent_id.name,
        'appraisal_objective_list': appraisal_objective_list,
        'company_info': company_info,
    }



def paging(data, flag1 = 0, flag2 = 0):        
    if flag1 == 1:
        return config.list12
    elif flag2 == 1:
        config.list12.clear()
    else:
        k = []
        for rec in data:
            for ids in rec:
                config.list12.append(ids.id)        
        
class CreateAppraisal(http.Controller):
    
    @http.route('/appraisal/feedback/data/save',type="http", website=True, auth='user')
    def appraisal_feedback_data_objective_template(self, **kw):
        feedback = request.env['hr.appraisal.feedback'].sudo().search([('id','=',int(kw.get('record_id')))])
        if feedback.name.department_id.manager_id.user_id.id==http.request.env.context.get('uid'):
            if kw.get('full_year_value_comment'):
                feedback.update({
                    'full_year_value_comment': kw.get('full_year_value_comment')
                })
            if kw.get('reason_for_disagreement'):
                feedback.update({
                    'reason_for_disagreement': kw.get('reason_for_disagreement')
                })
            if kw.get('full_reason_for_disagreement'):
                feedback.update({
                    'full_reason_for_disagreement': kw.get('full_reason_for_disagreement')
                })    
                
            if kw.get('full_year_value_comment'):
                feedback.update({
                    'full_year_value_comment': kw.get('full_year_value_comment')
                })
            if kw.get('full_year_appraiser_objective_comment'):
                feedback.update({
                    'full_year_appraiser_objective_comment': kw.get('full_year_appraiser_objective_comment')
                })
            if kw.get('full_year_appraiser_value_comment'):
                feedback.update({
                    'full_year_appraiser_value_comment': kw.get('full_year_appraiser_value_comment')
                })
            if kw.get('strength_1'):
                feedback.update({
                    'strength_1': kw.get('strength_1')
                })
            if kw.get('strength_2'):
                feedback.update({
                    'strength_2': kw.get('strength_2')
                })
            if kw.get('strength_3'):
                feedback.update({
                    'strength_3': kw.get('strength_3')
                })
            if kw.get('strength_4'):
                feedback.update({
                    'strength_4': kw.get('strength_4')
                })
            if kw.get('strength_5'):
                feedback.update({
                    'strength_5': kw.get('strength_5')
                })
            if kw.get('improvements_1'):
                feedback.update({
                    'improvements_1': kw.get('improvements_1')
                })
            if kw.get('improvements_2'):
                feedback.update({
                    'improvements_2': kw.get('improvements_2')
                })
            if kw.get('improvements_3'):
                feedback.update({
                    'improvements_3': kw.get('improvements_3')
                })
            if kw.get('improvements_4'):
                feedback.update({
                    'improvements_4': kw.get('improvements_4')
                })
            if kw.get('improvements_5'):
                feedback.update({
                    'improvements_5': kw.get('improvements_5')
                }) 
            if kw.get('training_1'):
                feedback.update({
                    'training_1': kw.get('training_1')
                })
            if kw.get('training_2'):
                feedback.update({
                    'training_2': kw.get('training_2')
                })
            if kw.get('training_3'):
                feedback.update({
                    'training_3': kw.get('training_3')
                })
            if kw.get('training_4'):
                feedback.update({
                    'training_4': kw.get('training_4')
                })
            if kw.get('training_5'):
                feedback.update({
                    'training_5': kw.get('training_5')
                }) 
            if kw.get('reason_1'):
                feedback.update({
                    'reason_1': kw.get('reason_1')
                })
            if kw.get('reason_2'):
                feedback.update({
                    'reason_2': kw.get('reason_2')
                })
            if kw.get('reason_3'):
                feedback.update({
                    'reason_3': kw.get('reason_3')
                })
            if kw.get('reason_4'):
                feedback.update({
                    'reason_4': kw.get('reason_4')
                })
            if kw.get('reason_5'):
                feedback.update({
                    'reason_5': kw.get('reason_5')
                })
            if kw.get('recommend_promotion'):
                if kw.get('recommend_promotion') !='blank':
                    feedback.update({
                        'recommend_promotion': kw.get('recommend_promotion')
                    })
            if kw.get('promotion_grade'):
                if kw.get('promotion_grade') !='blank':
                    feedback.update({
                        'promotion_grade': kw.get('promotion_grade')
                    })
            if kw.get('date_effective'):
                feedback.update({
                        'date_effective': kw.get('date_effective')
                    })          
        if feedback.name.parent_id.user_id.id==http.request.env.context.get('uid'):
            if kw.get('full_year_value_comment'):
                feedback.update({
                    'full_year_value_comment': kw.get('full_year_value_comment')
                })
            if kw.get('full_year_value_comment'):
                feedback.update({
                    'full_year_value_comment': kw.get('full_year_value_comment')
                })
            if kw.get('full_year_appraiser_objective_comment'):
                feedback.update({
                    'full_year_appraiser_objective_comment': kw.get('full_year_appraiser_objective_comment')
                })
            if kw.get('full_year_appraiser_value_comment'):
                feedback.update({
                    'full_year_appraiser_value_comment': kw.get('full_year_appraiser_value_comment')
                })
            if kw.get('strength_1'):
                feedback.update({
                    'strength_1': kw.get('strength_1')
                })
            if kw.get('strength_2'):
                feedback.update({
                    'strength_2': kw.get('strength_2')
                })
            if kw.get('strength_3'):
                feedback.update({
                    'strength_3': kw.get('strength_3')
                })
            if kw.get('strength_4'):
                feedback.update({
                    'strength_4': kw.get('strength_4')
                })
            if kw.get('strength_5'):
                feedback.update({
                    'strength_5': kw.get('strength_5')
                })
            if kw.get('improvements_1'):
                feedback.update({
                    'improvements_1': kw.get('improvements_1')
                })
            if kw.get('improvements_2'):
                feedback.update({
                    'improvements_2': kw.get('improvements_2')
                })
            if kw.get('improvements_3'):
                feedback.update({
                    'improvements_3': kw.get('improvements_3')
                })
            if kw.get('improvements_4'):
                feedback.update({
                    'improvements_4': kw.get('improvements_4')
                })
            if kw.get('improvements_5'):
                feedback.update({
                    'improvements_5': kw.get('improvements_5')
                }) 
            if kw.get('training_1'):
                feedback.update({
                    'training_1': kw.get('training_1')
                })
            if kw.get('training_2'):
                feedback.update({
                    'training_2': kw.get('training_2')
                })
            if kw.get('training_3'):
                feedback.update({
                    'training_3': kw.get('training_3')
                })
            if kw.get('training_4'):
                feedback.update({
                    'training_4': kw.get('training_4')
                })
            if kw.get('training_5'):
                feedback.update({
                    'training_5': kw.get('training_5')
                }) 
            if kw.get('reason_1'):
                feedback.update({
                    'reason_1': kw.get('reason_1')
                })
            if kw.get('reason_2'):
                feedback.update({
                    'reason_2': kw.get('reason_2')
                })
            if kw.get('reason_3'):
                feedback.update({
                    'reason_3': kw.get('reason_3')
                })
            if kw.get('reason_4'):
                feedback.update({
                    'reason_4': kw.get('reason_4')
                })
            if kw.get('reason_5'):
                feedback.update({
                    'reason_5': kw.get('reason_5')
                })
            if kw.get('recommend_promotion'):
                if kw.get('recommend_promotion') !='blank':
                    feedback.update({
                        'recommend_promotion': kw.get('recommend_promotion')
                    })
            if kw.get('promotion_position'):
                if kw.get('promotion_position') !='blank':
                    feedback.update({
                        'promotion_position': kw.get('promotion_position')
                    })
            if kw.get('date_effective'):
                feedback.update({
                        'date_effective': kw.get('date_effective')
                    })        
        if feedback.name.user_id.id==http.request.env.context.get('uid'):
            if kw.get('agreement'):
                if kw.get('agreement') != 'blank':
                    feedback.update({
                        'agreement': kw.get('agreement')
                    })
            if kw.get('full_year_agreement'):
                if kw.get('full_year_agreement') != 'blank':
                    feedback.update({
                        'full_year_agreement': kw.get('full_year_agreement')
                    })        
            if kw.get('objective_comment'):
                feedback.update({
                    'objective_comment': kw.get('objective_comment')
                })    
            if kw.get('value_comment'):
                feedback.update({
                    'value_comment': kw.get('value_comment')
                })
            if kw.get('half_year_appraiser_objective_comment'):
                feedback.update({
                    'half_year_appraiser_objective_comment': kw.get('half_year_appraiser_objective_comment')
                })
            if kw.get('half_year_appraiser_value_comment'):
                feedback.update({
                    'half_year_appraiser_value_comment': kw.get('half_year_appraiser_value_comment')
                }) 
            if kw.get('training_need'):
                feedback.update({
                    'training_need': kw.get('training_need')
                }) 
            if kw.get('future_aspiration'):
                feedback.update({
                    'future_aspiration': kw.get('future_aspiration')
                })
            if kw.get('feedback_to_manager'):
                feedback.update({
                    'feedback_to_manager': kw.get('feedback_to_manager')
                })    
        return request.redirect('/appraisal/feedback/%s'%(feedback.id))
    
    
    
    @http.route('/update/obj/feedback/line/save',type="http", website=True, auth='user')
    def update_appraisal_objective_template(self, **kw):
        half_year_objectvieline = request.env['hr.appraisal.feedback.objective.appraisee.line'].sudo().search([('id','=',int(kw.get('line_id')))])
        if half_year_objectvieline.feedback_id.name.parent_id.user_id.id==http.request.env.context.get('uid'):
            if kw.get('manager_rating_level'):
                half_year_objectvieline.update({
                    'manager_rating_level': kw.get('manager_rating_level')
                })
            if kw.get('remarks_mngr'):
                half_year_objectvieline.update({
                    'remarks_mngr': kw.get('remarks_mngr')
                })
            if kw.get('full_year_objective_comment'):
                half_year_objectvieline.feedback_id.update({
                    'full_year_objective_comment': kw.get('full_year_objective_comment')
                })   
        if half_year_objectvieline.feedback_id.name.user_id.id==http.request.env.context.get('uid'):
            if kw.get('employee_rating_level'):
                half_year_objectvieline.update({
                    'employee_rating_level': kw.get('employee_rating_level')
                })
            if kw.get('remarks'):
                half_year_objectvieline.update({
                    'remarks': kw.get('remarks')
                })
            if kw.get('objective_comment'):
                half_year_objectvieline.feedback_id.update({
                    'objective_comment': kw.get('objective_comment')
                })           
        return request.redirect('/appraisal/feedback/%s'%(half_year_objectvieline.feedback_id.id))
    
    
        
    @http.route('/update/fullyear/values/line/save',type="http", website=True, auth='user')
    def update_fullyear_values_template(self, **kw):
        full_year_coreline = request.env['hr.appraisal.feedback.values.line'].sudo().search([('id','=',int(kw.get('line_id')))])
        if full_year_coreline.feedback_id.name.parent_id.user_id.id==http.request.env.context.get('uid'):
            if kw.get('manager_rating_level'):
                full_year_coreline.update({
                    'manager_rating_level': kw.get('manager_rating_level')
                })
            if kw.get('full_remarks_mngr'):
                full_year_coreline.update({
                    'full_remarks_mngr': kw.get('full_remarks_mngr')
                })
            if kw.get('full_year_appraiser_value_comment'):
                full_year_coreline.feedback_id.update({
                    'full_year_appraiser_value_comment': kw.get('full_year_appraiser_value_comment')
                })   
        if full_year_coreline.feedback_id.name.user_id.id==http.request.env.context.get('uid'):
            if kw.get('employee_rating_level'):
                full_year_coreline.update({
                    'employee_rating_level': kw.get('employee_rating_level')
                })
            if kw.get('full_remarks'):
                full_year_coreline.update({
                    'full_remarks': kw.get('full_remarks')
                })
            if kw.get('half_year_appraiser_value_comment'):
                full_year_coreline.feedback_id.update({
                    'half_year_appraiser_value_comment': kw.get('half_year_appraiser_value_comment')
                })           
        return request.redirect('/appraisal/feedback/%s'%(full_year_coreline.feedback_id.id)) 
    
    
    @http.route('/update/values/feedback/line/save',type="http", website=True, auth='user')
    def update_appraisal_values_template(self, **kw):
        full_year_objectvieline = request.env['hr.appraisal.feedback.objective.line'].sudo().search([('id','=',int(kw.get('line_id')))])
        if full_year_objectvieline.feedback_id.name.parent_id.user_id.id==http.request.env.context.get('uid'):
            if kw.get('manager_rating_level'):
                full_year_objectvieline.update({
                    'manager_rating_level': kw.get('manager_rating_level')
                })
            if kw.get('full_remarks_mngr'):
                full_year_objectvieline.update({
                    'full_remarks_mngr': kw.get('full_remarks_mngr')
                })
            if kw.get('full_year_appraiser_objective_comment'):
                full_year_objectvieline.feedback_id.update({
                    'full_year_appraiser_objective_comment': kw.get('full_year_appraiser_objective_comment')
                })   
        if full_year_objectvieline.feedback_id.name.user_id.id==http.request.env.context.get('uid'):
            if kw.get('employee_rating_level'):
                full_year_objectvieline.update({
                    'employee_rating_level': kw.get('employee_rating_level')
                })
            if kw.get('full_remarks'):
                full_year_objectvieline.update({
                    'full_remarks': kw.get('full_remarks')
                })
            if kw.get('half_year_appraiser_objective_comment'):
                full_year_objectvieline.feedback_id.update({
                    'half_year_appraiser_objective_comment': kw.get('half_year_appraiser_objective_comment')
                })           
        return request.redirect('/appraisal/feedback/%s'%(full_year_objectvieline.feedback_id.id))
    
    
    
    @http.route('/update/obj/values/line/save',type="http", website=True, auth='user')
    def update_values_appraisal_objective_template(self, **kw):
        half_year_objectvieline = request.env['hr.appraisal.feedback.values.appraisee.line'].sudo().search([('id','=',int(kw.get('line_id')))])
        if half_year_objectvieline.feedback_id.name.parent_id.user_id.id==http.request.env.context.get('uid'):
            if kw.get('manager_rating_level'):
                half_year_objectvieline.update({
                    'manager_rating_level': kw.get('manager_rating_level')
                })
            if kw.get('remarks_mngr'):
                half_year_objectvieline.update({
                    'remarks_mngr': kw.get('remarks_mngr')
                })
            if kw.get('full_year_value_comment'):
                half_year_objectvieline.feedback_id.update({
                    'full_year_value_comment': kw.get('full_year_value_comment')
                })   
        if half_year_objectvieline.feedback_id.name.user_id.id==http.request.env.context.get('uid'):
            if kw.get('employee_rating_level'):
                half_year_objectvieline.update({
                    'employee_rating_level': kw.get('employee_rating_level')
                })
            if kw.get('remarks'):
                half_year_objectvieline.update({
                    'remarks': kw.get('remarks')
                })
            if kw.get('value_comment'):
                half_year_objectvieline.feedback_id.update({
                    'value_comment': kw.get('value_comment')
                })           
        return request.redirect('/appraisal/feedback/%s'%(half_year_objectvieline.feedback_id.id))    
    
    @http.route('/appraisal/objective/create/',type="http", website=True, auth='user')
    def appraisal_objective_template(self, **kw):
        global appraisal_objective_list
        appraisal_objective_list = []
        active_user = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
        active_employee = request.env['hr.employee'].search([('user_id','=',active_user.id)], limit=1)
        if active_employee.company_id.id==2 and active_employee.id != 4308:
            return request.render("de_portal_appraisal.re_appraisal_submited_expire",{})
        return request.render("de_portal_appraisal.submit_appraisal_objective",appraisal_page_content()) 
    
    @http.route('/add/obj/line/save',type="http", website=True, auth='user')
    def edit_existing_objective_template(self, **kw):
        line_id = kw.get('line_id')
        exist_line_obj = request.env['hr.appraisal.objective.line'].search([('id','=',line_id)])
        exist_line_obj.update({
            'objective': kw.get('objective'),
            'description': kw.get('objective'),
            'weightage': kw.get('weightage'),
            'date_from': kw.get('date_from'),
            'date_to': kw.get('date_to'),
        })
        if kw.get('status_id'):
            if kw.get('status_id') !='blank':
                exist_line_obj.update({
                    'status_id': kw.get('status_id'),
                })
        if kw.get('category_id'):
            if kw.get('category_id') !='blank':
                exist_line_obj.update({
                  'category_id': kw.get('category_id'),
                })        
        if kw.get('measuring_indicator'):
            exist_line_obj.update({
                'measuring_indicator': kw.get('measuring_indicator'),
            })
        if kw.get('priority') :
            if kw.get('priority') != 'blank':
                exist_line_obj.update({
                    'priority': kw.get('priority'),
                })    
        return request.redirect('/appraisal/objective/%s'%(exist_line_obj.objective_id.id))
    
    
    @http.route('/add/objective/line/save',type="http", website=True, auth='user')
    def add_appraisal_objective_template_submit(self, **kw):
        objecitve_id = kw.get('rec_id')
        exist_obj = request.env['hr.appraisal.objective'].search([('id','=',objecitve_id)])
        line_vals = {
            'objective_id': exist_obj.id,
            'category_id': kw.get('category_id'),
            'objective': kw.get('objective'),
            'description': kw.get('objective'),
            'weightage': kw.get('weightage'),
            'date_from': kw.get('date_from'),
            'date_to': kw.get('date_to'),
        }
        obj_line=request.env['hr.appraisal.objective.line'].sudo().create(line_vals)
        if kw.get('measuring_indicator'):
            obj_line.update({
                'measuring_indicator': kw.get('measuring_indicator'),
            })
        if kw.get('priority'):
            if kw.get('priority') != 'blank':
                obj_line.update({
                    'priority': kw.get('priority'),
                }) 
        if kw.get('status_id'):
            obj_line.update({
            'status_id': kw.get('status_id'),
            })     
        return request.redirect('/appraisal/objective/%s'%(exist_obj.id))
    
    @http.route('/update/appraisal/feedback/save',type="http", website=True, auth='user')
    def update_appraisal_feedback_template_submit(self, **kw):
        feedback_id = int(kw.get('ffeedback_id'))
        exist_obj = request.env['hr.appraisal.feedback'].search([('id','=',feedback_id)])
        if exist_obj.name.user_id.id ==  http.request.env.context.get('uid'):
            exist_obj.update({
                'future_aspiration': kw.get('future_aspiration'),
                'training_need': kw.get('training_need'),
                'feedback_to_manager': kw.get('feedback_to_manager'),
            })
       
        return request.render("de_portal_appraisal.appraisal_submited", {})
    
    
    
    
    @http.route('/halfyear/feedback/objective/edit/',type="http", website=True, auth='user')
    def halfyear_feedback_objective_template(self, **kw):
        global halfyear_objective_list
        halfyear_objective_list = []
        return request.render("de_portal_appraisal.edit_feedback_objective",appraisal_page_content()) 
    
    
    
    @http.route('/appraisal/objective/save', type="http", auth="public", website=True)
    def submit_objective_setting(self, **kw):
        record = request.env['hr.appraisal.objective'].sudo().search([('id','=',int(kw.get('record_id')))])  
        line_count = 0
        for line in record.objective_lines:
            line_count += 1
        if line_count < 3:
            raise UserError(('At least 3 objectives require to Submit Objective Setting (Minimum=3, Maximum=8)'))
        if line_count > 8:
            raise UserError(_('Maximum 8 objectives require to Submit Objective Setting (Minimum=3, Maximum=8)')) 
        if record.total_weightage != 100:
            raise UserError('Total Weightage must be equal 100')
        if record.state == 'draft':    
            record.action_sent_review()    
        return request.render("de_portal_appraisal.appraisal_submited", {})
    
    @http.route('/appraisal/extra/objective/save', type="http", auth="public", website=True)
    def extra_submit_objective_setting(self, **kw):
        record = request.env['hr.appraisal.objective'].sudo().search([('id','=',int(kw.get('records_id')))])
        if kw.get('description'):
            record.update({
                'description': kw.get('description')
            })  
        if kw.get('traing_need'):
            record.update({
                'traing_need': kw.get('traing_need')
            })      
        line_count = 0
        for line in record.objective_lines:
            line_count += 1
        if line_count < 3:
            raise UserError(('At least 3 objectives require to Submit Objective Setting (Minimum=3, Maximum=8)'))
        if line_count > 8:
            raise UserError(_('Maximum 8 objectives require to Submit Objective Setting (Minimum=3, Maximum=8)')) 
        if record.total_weightage != 100:
            raise UserError('Total Weightage must be equal 100')  
        
        return request.redirect('/appraisal/objective/%s'%(record.id))
    
    

    @http.route('/new/objective/save', type="http", auth="public", website=True)
    def new_objective_setting_submit(self, **kw):
        vals ={
            'employee_id': kw.get('employee_id'),
            'objective_year': kw.get('objective_year'),
            'traing_need':  kw.get('traing_need'),
            'description':  kw.get('description'),
        }
        record = request.env['hr.appraisal.objective'].sudo().create(vals)
        return request.redirect('/edit/add/objective/line/%s'%(record.id))

    
    
    @http.route('/appraisal/create/',type="http", website=True, auth='user')
    def appraisal_template(self, **kw):
        global appraisal_objective_list
        appraisal_objective_list = []
        return request.render("de_portal_appraisal.portal_appraisal",appraisal_page_content()) 
    
   
    
   
class CustomerPortal(CustomerPortal):
    
    
    @http.route(['/edit/objective/line/<int:line_id>'], type='http', auth="user", website=True)
    def edit_objective_line_template(self, line_id, access_token=None, **kw):
        values = {}
        active_user = http.request.env.context.get('uid')
        appraisal_user = []
        id = line_id
        try:
            appraisal_sudo = request.env['hr.appraisal.objective.line'].sudo().search([('id','=', line_id)]), 
        except (AccessError, MissingError):
            return request.redirect('/my')   
        obj_line_sudo = request.env['hr.appraisal.objective.line'].sudo().search([('id','=', line_id)])
        return request.render("de_portal_appraisal.edit_object_appraisal_objective", appraisal_page_content_edit(line_id))
    
    
    
    @http.route(['/delete/objective/line/<int:line_id>'], type='http', auth="user", website=True)
    def delete_objective_line_template(self, line_id, access_token=None, **kw):
        values = {}
        active_user = http.request.env.context.get('uid')
        appraisal_user = []
        id = line_id
        try:
            appraisal_sudo = request.env['hr.appraisal.objective.line'].sudo().search([('id','=', line_id)]), 
        except (AccessError, MissingError):
            return request.redirect('/my')   
        obj_line_sudo = request.env['hr.appraisal.objective.line'].sudo().search([('id','=', line_id)])
        recid = obj_line_sudo.objective_id
        obj_line_sudo.unlink()
        return request.redirect('/appraisal/objective/%s'%(recid.id))

    
    
    @http.route(['/edit/add/objective/line/<int:appraisal_id>'], type='http', auth="user", website=True)
    def get_appraisal_edit_objective_line_template(self, appraisal_id, access_token=None, **kw):
        values = []
        active_user = http.request.env.context.get('uid')
        appraisal_user = []
        id = appraisal_id
        try:
            appraisal_sudo = self._document_check_access('hr.appraisal.objective', appraisal_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')        

        appraisal_user_flag = 0
                
        appraisal_id_list = paging(0,1,0)
        next_id = 0
        pre_id = 0
        next_next_id = 0
        appraisal_id_list.sort()
        length_list = len(appraisal_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if appraisal_id in appraisal_id_list:
                appraisal_id_loc = appraisal_id_list.index(appraisal_id)
                if appraisal_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif appraisal_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0
        manager_objective = False
        edit_objective = True
        if appraisal_sudo.employee_id.parent_id.user_id.id == active_user:
            manager_objective = True
        values = self._appraisal_edit_get_page_view_values(appraisal_sudo, edit_objective,manager_objective, next_id, pre_id, appraisal_user_flag,access_token, **kw)
        exist_obj = request.env['hr.appraisal.objective'].sudo().search([('id','=',appraisal_id)])
        values.update({
            'exist_obj': appraisal_sudo,
        })
        return request.render("de_portal_appraisal.add_object_appraisal_objective", values)
    
    
    @http.route(['/action/confirm/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_confirm(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.feedback'].sudo().browse(id)

        record.action_confirm()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.feedback', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._feedback_get_page_view_values(approval_sudo, **kw) 
        return request.redirect('/appraisal/feedback/%s'%(record.id))
    
    @http.route(['/action/reset/hod/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_reset(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.feedback'].sudo().browse(id)

        record.action_refuse()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.feedback', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._feedback_get_page_view_values(approval_sudo, **kw) 
        return request.redirect('/appraisal/feedback/%s'%(record.id))
    
    @http.route(['/action/confirm/objective/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_confirm_objective(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.objective'].sudo().browse(id)

        record.action_submit()
        try:
            obj_sudo = self._document_check_access('hr.appraisal.objective', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._appraisal_get_page_view_values(obj_sudo, **kw) 
        return request.redirect('/appraisal/objective/%s'%(record.id))
    
    @http.route(['/action/reset/objective/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_reset_objective(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.objective'].sudo().browse(id)

        record.action_reset()
        try:
            obj_sudo = self._document_check_access('hr.appraisal.objective', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._appraisal_get_page_view_values(obj_sudo, **kw) 
        return request.redirect('/appraisal/objective/%s'%(record.id))
    
    
    @http.route(['/action/sent/hr/review/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_Sent_for_Employee_Review(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.feedback'].sudo().browse(id)

        record.action_Sent_for_Employee_Review()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.feedback', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._feedback_get_page_view_values(approval_sudo, **kw) 
        return request.redirect('/appraisal/feedback/%s'%(record.id))
    
    @http.route(['/action/endorsed/hr/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_endorsed_employee(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.feedback'].sudo().browse(id)

        record.action_endorsed_employee()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.feedback', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._feedback_get_page_view_values(approval_sudo, **kw) 
        return request.redirect('/appraisal/feedback/%s'%(record.id))
    
    @http.route(['/action/endorsed/hr/hod/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_endorsed_hod(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.feedback'].sudo().browse(id)

        record.action_endorsed_hod()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.feedback', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._feedback_get_page_view_values(approval_sudo, **kw) 
        return request.redirect('/appraisal/feedback/%s'%(record.id))
    
    
    @http.route(['/action/appraiser/review/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_end_year_appraiser_review(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.feedback'].sudo().browse(id)

        record.action_end_year_appraiser_review()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.feedback', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._feedback_get_page_view_values(approval_sudo, **kw) 
        return request.redirect('/appraisal/feedback/%s'%(record.id))
    
    @http.route(['/action/end/appraiser/review/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_end_year_sent_emp_view(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.feedback'].sudo().browse(id)

        record.action_end_year_sent_emp_view()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.feedback', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._feedback_get_page_view_values(approval_sudo, **kw) 
        return request.redirect('/appraisal/feedback/%s'%(record.id))
    
    
    @http.route(['/action/end/endoresd/review/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_end_year_endorsed_emp(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.feedback'].sudo().browse(id)

        record.action_end_year_endorsed_emp()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.feedback', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._feedback_get_page_view_values(approval_sudo, **kw) 
        return request.redirect('/appraisal/feedback/%s'%(record.id))
    
    
    @http.route(['/action/end/endoresd/hod/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_end_year_endorse_hod(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.feedback'].sudo().browse(id)

        record.action_end_year_endorse_hod()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.feedback', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._feedback_get_page_view_values(approval_sudo, **kw) 
        return request.redirect('/appraisal/feedback/%s'%(record.id))
        
    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'objective_count' in counters:
            values['objective_count'] = request.env['hr.appraisal.objective'].search_count([('employee_id.user_id', '=', http.request.env.context.get('uid') )])
        return values
  
    def _appraisal_get_page_view_values(self,appraisal, next_id = 0,pre_id= 0, appraisal_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
        categories = request.env['hr.objective.category'].sudo().search([])
        employees = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
        status = request.env['hr.objective.status'].sudo().search([])
        exist_obj = request.env['hr.appraisal.objective'].sudo().search([('id','=',appraisal.id)])
        values = {
            'page_name' : 'appraisal',
            'appraisal' : appraisal,
            'categories': categories,
            'employee_name': appraisal.employee_id,
            'managers': appraisal.employee_id.parent_id.name,
            'exist_obj': exist_obj,
            'status': status,
            'edit_objective': False,
            'manager_objective': False,
            'appraisal_user_flag': appraisal_user_flag,
            'next_id' : next_id,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(appraisal, access_token, values, 'my_appraisal_history', False, **kwargs)

    def _appraisal_edit_get_page_view_values(self,appraisal, edit_objective,manager_objective, next_id = 0,pre_id= 0, appraisal_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
        categories = request.env['hr.objective.category'].sudo().search([])
        employees = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
        status = request.env['hr.objective.status'].sudo().search([])
        values = {
            'page_name' : 'appraisal',
            'appraisal' : appraisal,
            'categories': categories,
            'employee_name': appraisal.employee_id,
            'managers': appraisal.employee_id.parent_id.name,
            'status': status,
            'appraisal_user_flag': appraisal_user_flag,
            'next_id' : next_id,
             'edit_objective': edit_objective,
            'manager_objective': manager_objective,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(appraisal, access_token, values, 'my_appraisal_history', False, **kwargs)

    
    @http.route(['/appraisal/objectives', '/appraisal/objective/page/<int:page>'], type='http', auth="user", website=True)
    def portal_appraisal_objectives(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'id': {'label': _('Default'), 'order': 'id asc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft', 'waiting','confirm'])]},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'waiting': {'label': _('Submitted'), 'domain': [('state', '=', 'waiting')]},  
            'confirmed': {'label': _('Approved'), 'domain': [('state', '=', 'confirm')]},
        }
           
        searchbar_inputs = {
            'id': {'input': 'id', 'label': _('Search in No#')},
            'name': {'input': 'name', 'label': _('Search in Name')},
            'employee_id.name': {'input': 'employee_id.name', 'label': _('Search in Employee')}, 
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

        appraisal_groups = request.env['hr.appraisal.objective'].sudo().search([])

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
#         domain = []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]       

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            if search_in in ('employee_id.name', 'all'):
                search_domain = OR([search_domain, [('employee_id.name', 'ilike', search)]])
            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain
        domain += ['|',('employee_id.user_id', '=', http.request.env.context.get('uid')),('employee_id.parent_id.user_id', '=', http.request.env.context.get('uid'))]    
 
        appraisal_count = request.env['hr.appraisal.objective'].sudo().search_count(domain)

        pager = portal_pager(
            url="/appraisal/objectives",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=appraisal_count,
            page=page,
            step=self._items_per_page
        )

        _appraisals = request.env['hr.appraisal.objective'].sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_appraisal_history'] = _appraisals.ids[:100]

        grouped_appraisals = [_appraisals]
                
        paging(0,0,1)

        paging(grouped_appraisals)
        company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_appraisals': grouped_appraisals,
            'page_name': 'appraisal',
            'default_url': '/appraisal/objectives',
            'pager': pager,
            'company_info': company_info,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        })
        return request.render("de_portal_appraisal.portal_appraisal_objectives", values)

   
    @http.route(['/appraisal/objective/<int:appraisal_id>'], type='http', auth="user", website=True)
    def portal_appraisal_objective(self, appraisal_id, access_token=None, **kw):
        values = []
        active_user = http.request.env.context.get('uid')
        appraisal_user = []
        id = appraisal_id
        try:
            appraisal_sudo = self._document_check_access('hr.appraisal.objective', appraisal_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')        

        appraisal_user_flag = 0
                
        appraisal_id_list = paging(0,1,0)
        next_id = 0
        pre_id = 0
        next_next_id = 0
        appraisal_id_list.sort()
        length_list = len(appraisal_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if appraisal_id in appraisal_id_list:
                appraisal_id_loc = appraisal_id_list.index(appraisal_id)
                if appraisal_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif appraisal_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0
            

        values = self._appraisal_get_page_view_values(appraisal_sudo,next_id, pre_id, appraisal_user_flag,access_token, **kw) 
        return request.render("de_portal_appraisal.portal_appraisal_objective", values)
    
    
    # Appraisal Edit Objective
    
    @http.route(['/appraisal/edit/objective/<int:appraisal_id>'], type='http', auth="user", website=True)
    def edit_portal_appraisal_objective(self, appraisal_id, access_token=None, **kw):
        values = []
        active_user = http.request.env.context.get('uid')
        appraisal_user = []
        id = appraisal_id
        try:
            appraisal_sudo = self._document_check_access('hr.appraisal.objective', appraisal_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')        

        appraisal_user_flag = 0
                
        appraisal_id_list = paging(0,1,0)
        next_id = 0
        pre_id = 0
        next_next_id = 0
        appraisal_id_list.sort()
        length_list = len(appraisal_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if appraisal_id in appraisal_id_list:
                appraisal_id_loc = appraisal_id_list.index(appraisal_id)
                if appraisal_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif appraisal_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0
        manager_objective = False
        edit_objective = True
        if appraisal_sudo.employee_id.parent_id.user_id.id == active_user:
            manager_objective = True
        values = self._appraisal_edit_get_page_view_values(appraisal_sudo, edit_objective,manager_objective, next_id, pre_id, appraisal_user_flag,access_token, **kw) 
        return request.render("de_portal_appraisal.portal_appraisal_objective", values)
    



################################################################
#         Appraisal FeedBack
################################################################

    @http.route(['/edit/feedback/full/year/line/<int:line_id>'], type='http', auth="user", website=True)
    def edit_feedback_fullyear_line_template(self, line_id, access_token=None, **kw):
        values = {}
        active_user = http.request.env.context.get('uid')
        appraisal_user = []
        id = line_id
        try:
            appraisal_sudo = request.env['hr.appraisal.feedback.objective.line'].sudo().search([('id','=', line_id)]), 
        except (AccessError, MissingError):
            return request.redirect('/my')   
        obj_line_sudo = request.env['hr.appraisal.feedback.objective.line'].sudo().search([('id','=', line_id)])
        manager_edit = False
        user_edit = False
        if obj_line_sudo.feedback_id.name.parent_id.user_id.id == http.request.env.context.get('uid'):
            manager_edit = True
        if obj_line_sudo.feedback_id.name.user_id.id == http.request.env.context.get('uid'):
            user_edit = True    
        return request.render("de_portal_appraisal.edit_full_year_objective_line", appraisal_full_year_obj_page_content_edit(line_id, manager_edit, user_edit))
    
    
    @http.route(['/edit/fullyear/values/line/<int:line_id>'], type='http', auth="user", website=True)
    def edit_fullyear_values_line_template(self, line_id, access_token=None, **kw):
        values = {}
        active_user = http.request.env.context.get('uid')
        appraisal_user = []
        id = line_id
        try:
            appraisal_sudo = request.env['hr.appraisal.feedback.values.line'].sudo().search([('id','=', line_id)]), 
        except (AccessError, MissingError):
            return request.redirect('/my')   
        obj_line_sudo = request.env['hr.appraisal.feedback.values.line'].sudo().search([('id','=', line_id)])
        manager_edit = False
        user_edit = False
        if obj_line_sudo.feedback_id.name.parent_id.user_id.id == http.request.env.context.get('uid'):
            manager_edit = True
        if obj_line_sudo.feedback_id.name.user_id.id == http.request.env.context.get('uid'):
            user_edit = True    
        return request.render("de_portal_appraisal.edit_full_year_value_line", appraisal_full_year_values_page_content_edit(line_id, manager_edit, user_edit))
    

    @http.route(['/edit/feedback/objective/line/<int:line_id>'], type='http', auth="user", website=True)
    def edit_feedback_objective_line_template(self, line_id, access_token=None, **kw):
        values = {}
        active_user = http.request.env.context.get('uid')
        appraisal_user = []
        id = line_id
        try:
            appraisal_sudo = request.env['hr.appraisal.feedback.objective.appraisee.line'].sudo().search([('id','=', line_id)]), 
        except (AccessError, MissingError):
            return request.redirect('/my')   
        obj_line_sudo = request.env['hr.appraisal.feedback.objective.appraisee.line'].sudo().search([('id','=', line_id)])
        manager_edit = False
        user_edit = False
        if obj_line_sudo.feedback_id.name.parent_id.user_id.id == http.request.env.context.get('uid'):
            manager_edit = True
        if obj_line_sudo.feedback_id.name.user_id.id == http.request.env.context.get('uid'):
            user_edit = True    
        return request.render("de_portal_appraisal.edit_feedback_bussiness_objective_line", appraisal_feedback_page_content_edit(line_id, manager_edit, user_edit))
    
    
    @http.route(['/edit/feedback/values/line/<int:line_id>'], type='http', auth="user", website=True)
    def edit_feedback_values_line_template(self, line_id, access_token=None, **kw):
        values = {}
        active_user = http.request.env.context.get('uid')
        appraisal_user = []
        id = line_id
        try:
            appraisal_sudo = request.env['hr.appraisal.feedback.values.appraisee.line'].sudo().search([('id','=', line_id)]), 
        except (AccessError, MissingError):
            return request.redirect('/my')   
        obj_line_sudo = request.env['hr.appraisal.feedback.values.appraisee.line'].sudo().search([('id','=', line_id)])
        manager_edit = False
        user_edit = False
        if obj_line_sudo.feedback_id.name.parent_id.user_id.id == http.request.env.context.get('uid'):
            manager_edit = True
        if obj_line_sudo.feedback_id.name.user_id.id == http.request.env.context.get('uid'):
            user_edit = True    
        return request.render("de_portal_appraisal.edit_feedback_values_objective_line", appraisal_feedback_values_page_content_edit(line_id, manager_edit, user_edit))
    
    
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'feedback_count' in counters:
            values['feedback_count'] = request.env['hr.appraisal.feedback'].search_count([('name.user_id', '=', http.request.env.context.get('uid') )])
        return values
  
    def _feedback_get_page_view_values(self,feedback, next_id = 0,pre_id= 0, feedback_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        employees = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
        grade_types = request.env['grade.designation'].sudo().search([])
        job_positions = request.env['hr.job'].sudo().search([('company_id','=',employees.company_id.id)])
        manager_edit = False
        edit_flag =  False
        review_flag = False
        values = {
            'page_name' : 'feedback',
            'feedback' : feedback,
            'review_flag': review_flag,
            'job_positions': job_positions,
            'grade_types': grade_types,
            'employee_name': feedback.name,
            'managers': feedback.name.parent_id.name,
            'manager_edit': manager_edit,
            'edit_flag': edit_flag,
            'full_review_flag': False,
            'full_manager_edit':False,
            'full_edit_flag': False,
            'feedback_user_flag': feedback_user_flag,
            'next_id' : next_id,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(feedback, access_token, values, 'my_feedback_history', False, **kwargs)
    
    
    def _edit_feedback_get_page_view_values(self,feedback, full_edit_flag, full_review_flag, full_manager_edit, manager_edit, edit_flag, review_flag, next_id = 0,pre_id= 0, feedback_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        grade_types = request.env['grade.designation'].sudo().search([])
        job_positions = request.env['hr.job'].sudo().search([('company_id','=',employees.company_id.id)])
        values = {
            'page_name' : 'feedback',
            'feedback' : feedback,
            'job_positions': job_positions,
            'grade_types': grade_types,
            'review_flag': review_flag,
            'employee_name': feedback.name,
            'managers': feedback.name.parent_id.name,
            'manager_edit': manager_edit,
            'edit_flag': edit_flag,
            'full_review_flag': full_review_flag,
            'full_manager_edit':full_manager_edit,
            'full_edit_flag': full_edit_flag,
            'feedback_user_flag': feedback_user_flag,
            'next_id' : next_id,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(feedback, access_token, values, 'my_feedback_history', False, **kwargs)

    @http.route(['/appraisals/feedback', '/appraisals/feedback/page/<int:page>'], type='http', auth="user", website=True)
    def portal_appraisals_feedback(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'id': {'label': _('Default'), 'order': 'id asc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft', 'expired','confirm','sent','endorsed_employee','endorsed_hod','done','end_year_appraisee_review',
'end_year_appraiser_review','end_year_sent_emp_view','end_year_endorsed_emp','end_yaer_endorse_hod','closed'])]},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'waiting': {'label': _('Expire'), 'domain': [('state', '=', 'expired')]},  
            'confirmed': {'label': _('Approved'), 'domain': [('state', '=', 'confirmed')]},
        }
           
        searchbar_inputs = {
            'id': {'input': 'id', 'label': _('Search in No#')},
            'name': {'input': 'name', 'label': _('Search in Name')},
            'name.name': {'input': 'name.name', 'label': _('Search in Employee')}, 
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

        feedback_groups = request.env['hr.appraisal.feedback'].sudo().search([])

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
#         domain = []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]       

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            if search_in in ('employee_id.name', 'all'):
                search_domain = OR([search_domain, [('name.name', 'ilike', search)]])
            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain
        domain += ['|','|',('name.user_id', '=', http.request.env.context.get('uid')),('name.parent_id.user_id', '=', http.request.env.context.get('uid')),('name.department_id.manager_id.user_id', '=', http.request.env.context.get('uid'))]     
        feedback_count = request.env['hr.appraisal.feedback'].sudo().search_count(domain)

        pager = portal_pager(
            url="/appraisals/feedback",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=feedback_count,
            page=page,
            step=self._items_per_page
        )

        _feedbacks = request.env['hr.appraisal.feedback'].sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_feedback_history'] = _feedbacks.ids[:100]

        grouped_feedbacks = [_feedbacks]
                
        paging(0,0,1)

        paging(grouped_feedbacks)
        company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_feedbacks': grouped_feedbacks,
            'page_name': 'feedback',
            'default_url': '/appraisals/feedback',
            'pager': pager,
            'company_info': company_info,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        })
        return request.render("de_portal_appraisal.portal_appraisal_feedbacks", values)
    
    
    @http.route(['/edit/appraisal/feedback/<int:feedback_id>'], type='http', auth="user", website=True)
    def edit_portal_appraisal_feedback(self, feedback_id, access_token=None, **kw):
        values = []
        active_user = http.request.env.context.get('uid')
        feedback_user = []
        id = feedback_id
        try:
            feedback_sudo = self._document_check_access('hr.appraisal.feedback', feedback_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')        

        feedback_user_flag = 0
                
        feedback_id_list = paging(0,1,0)
        next_id = 0
        pre_id = 0
        next_next_id = 0
        feedback_id_list.sort()
        length_list = len(feedback_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if feedback_id in feedback_id_list:
                feedback_id_loc = feedback_id_list.index(feedback_id)
                if feedback_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif feedback_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0
            
        edit_flag = False
        review_flag = False
        manager_edit = False
        if feedback_sudo.state == 'draft':           
            edit_flag = True
        if feedback_sudo.state == 'sent' and feedback_sudo.name.parent_id.user_id.id == http.request.env.context.get('uid'):                         manager_edit = True              
        if feedback_sudo.state == 'sent' and feedback_sudo.name.user_id.id == http.request.env.context.get('uid'):    
           review_flag = True 
        if feedback_sudo.state == 'end_year_sent_emp_view' and feedback_sudo.name.user_id.id == http.request.env.context.get('uid'):   
           review_flag = True   
        if feedback_sudo.state == 'confirm':              
            manager_edit = True 
        full_edit_flag = False
        full_review_flag = False
        full_manager_edit = False
        if feedback_sudo.state == 'end_year_appraisee_review' and feedback_sudo.name.user_id.id == http.request.env.context.get('uid'):           
            full_edit_flag = True
        if feedback_sudo.state == 'end_year_sent_emp_view' and feedback_sudo.name.user_id.id == http.request.env.context.get('uid'):              
            full_review_flag = True
        if feedback_sudo.state == 'end_year_appraiser_review'and feedback_sudo.name.parent_id.user_id.id == http.request.env.context.get('uid'):              
            full_manager_edit = True
        if feedback_sudo.state == 'end_year_sent_emp_view'and feedback_sudo.name.parent_id.user_id.id == http.request.env.context.get('uid'):              
            full_manager_edit = True    
        values = self._edit_feedback_get_page_view_values(feedback_sudo, full_edit_flag, full_review_flag, full_manager_edit, manager_edit, edit_flag, review_flag, next_id, pre_id, feedback_user_flag,access_token, **kw) 
        return request.render("de_portal_appraisal.portal_appraisal_feedback", values)

   
    @http.route(['/appraisal/feedback/<int:feedback_id>'], type='http', auth="user", website=True)
    def portal_appraisal_feedback(self, feedback_id, access_token=None, **kw):
        values = []
        active_user = http.request.env.context.get('uid')
        feedback_user = []
        id = feedback_id
        try:
            feedback_sudo = self._document_check_access('hr.appraisal.feedback', feedback_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')        

        feedback_user_flag = 0
                
        feedback_id_list = paging(0,1,0)
        next_id = 0
        pre_id = 0
        next_next_id = 0
        feedback_id_list.sort()
        length_list = len(feedback_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if feedback_id in feedback_id_list:
                feedback_id_loc = feedback_id_list.index(feedback_id)
                if feedback_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif feedback_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0
            
        
        values = self._feedback_get_page_view_values(feedback_sudo, next_id, pre_id, feedback_user_flag,access_token, **kw) 
        return request.render("de_portal_appraisal.portal_appraisal_feedback", values)

 