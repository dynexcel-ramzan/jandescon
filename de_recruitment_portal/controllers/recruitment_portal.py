# # -*- coding: utf-8 -*-
from . import config
from . import update
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError
from collections import OrderedDict
from operator import itemgetter
from datetime import datetime , date
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
import base64
import binascii

def recruitment_page_content(flag = 0):
#     employees = request.env['hr.employee'].search([('user_id','=',http.request.env.context.get('uid'))])
    company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    return {
        'employees' : employees,
        'success_flag' : flag,
        'company_info' : company_info
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
 
    
        
# class CreateRecruitment(http.Controller):

#     @http.route('/recruitment/create/',type="http", website=True, auth='user')
#     def timeoff_create_template(self, **kw):
#         return request.render("de_recruitment_portal.recruitment_template",recruitment_page_content()) 
#     
#     @http.route('/my/recruitment/save', type="http", auth="public", website=True)
#     def recruitment_submit_forms(self, **kw):
#         if kw.get('description'):
#             recruitment_val = {
#                 'employee_id': int(kw.get('employee_id')),            
#                 'recruitment_type':kw.get('recruitment_type'),
#                 'recruitment_reason': kw.get('recruitment_reason'),
#                 'expected_revealing_date': kw.get('last_day_of_employee'),
#                 'reason':kw.get('description'),
#             }
#             record = request.env['hr.recruitment.interviews'].sudo().create(recruitment_val)
#             record.confirm_recruitment()
#             
#         return request.render("de_recruitment_portal.recruitment_submitted", {}, recruitment_page_content())
  

    
    
    
class CustomerPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'recruitment_count' in counters:
            values['recruitment_count'] = request.env['hr.recruitment.interviews'].search_count([('employee_id.user_id', '=', http.request.env.context.get('uid') )])
        return values
  
    def _recruitment_get_page_view_values(self,recruitment, next_id = 0,pre_id= 0, recruitment_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values = {
            'page_name': 'recruitment',
            'recruitment': recruitment,
            'recruitment_user_flag':recruitment_user_flag,
            'next_id' : next_id,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(recruitment, access_token, values, 'my_recruitment_history', False, **kwargs)
    

    @http.route(['/my/recruitments', '/my/recruitments/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_recruitments(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby=None, **kw):
        
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'interviewer_id': {'label': _('Employee'), 'order': 'interviewer_id desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
                                 
        
        searchbar_inputs = {  
            'name': {'input': 'name', 'label': _('Search in Employee')},
            'id': {'input': 'id', 'label': _('Search in Ref#')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

        timeoff_groups = request.env['hr.recruitment.interviews'].search([])

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]       

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            domain += search_domain
        recruitment_count = request.env['hr.recruitment.interviews'].search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/recruitments",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'seissuesarch_in': search_in, 'search': search},
            total=555,
            page=page,
            step=self._items_per_page
        )

        _recruitment = request.env['hr.recruitment.interviews'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_recruitment_history'] = _recruitment.ids[:100]

        grouped_recruitments = [_recruitment]
                
        paging(0,0,1)
        paging(grouped_recruitments)
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_recruitments': grouped_recruitments,
            'page_name': 'recruitments',
            'default_url': '/my/recruitments',
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
        return request.render("de_recruitment_portal.portal_my_recruitments", values)   

   
    @http.route(['/my/recruitment/<int:recruitment_id>'], type='http', auth="user", website=True)
    def portal_my_recruitment(self, recruitment_id, access_token=None, **kw):
        try:
            recruitment_sudo = self._document_check_access('hr.recruitment.interviews', recruitment_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        next_id = 0
        pre_id = 0
        recruitment_user_flag = 0
                 
        recruitment_id_list = paging(0,1,0)
        next_next_id = 0
        recruitment_id_list.sort()
        length_list = len(recruitment_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if recruitment_id in recruitment_id_list:
                recruitment_id_loc = recruitment_id_list.index(recruitment_id)
                if recruitment_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif recruitment_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0
 
 
        values = self._recruitment_get_page_view_values(recruitment_sudo,next_id, pre_id,access_token, **kw) 
        return request.render("de_recruitment_portal.portal_my_recruitment", values)
    
    
#     @http.route(['/my/current/recruitment/<int:recruitment_id>'], type='http', auth="user", website=True)
#     def portal_my_recruitment_interview(self, recruitment_id, access_token=None, **kw):
#         try:
#             recruitment_sudo = self._document_check_access('hr.recruitment.interviews', recruitment_id, access_token)
#         except (AccessError, MissingError):
#             return request.redirect('/my')
        
        
#         if recruitment_sudo:
#             recruitment_sudo.action_start_survey()
    
    
    @http.route(['/my/current/recruitment/<int:recruitment_id>'], type='http', auth="public", website=True)
    def portal_my_recruitment_interview(self, recruitment_id, access_token=None, **kw):
        id=recruitment_id
        recrd = request.env['hr.recruitment.interviews'].sudo().browse(id)
        recrd.action_start_survey()
#         recruitment_page = CustomerPortal()
#         return request.render("de_portal_approvals.approval_submited", {})
    
    
    
    
    
 
    @http.route(['/recruitment/next/<int:recruitment_id>'], type='http', auth="user", website=True)
    def portal_my_next_recruitment(self, recruitment_id, access_token=None, **kw):
         
        recruitment_id_list = paging(0,1,0)
        next_next_id = 0
        recruitment_id_list.sort()
         
        length_list = len(recruitment_id_list)
        if length_list == 0:
            return request.redirect('/my')
        length_list = length_list - 1
         
        if recruitment_id in recruitment_id_list:
            recruitment_id_loc = recruitment_id_list.index(recruitment_id)
            next_next_id = recruitment_id_list[recruitment_id_loc + 1] 
            next_next_id_loc = recruitment_id_list.index(next_next_id)
            if next_next_id_loc == length_list:
                next_id = 0
                pre_id = 1
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in recruitment_id_list:
                if ids < timeoff_id:
                    buffer_smaller = ids
                if ids > timeoff_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_larger:
                next_next_id = buffer_smaller
            elif buffer_smaller:
                next_next_id = buffer_larger
                 
            next_next_id_loc = recruitment_id_list.index(next_next_id)
            length_list = len(recruitment_id_list)
            length_list = length_list + 1
            if next_next_id_loc == length_list:
                next_id = 0
                pre_id = 1
            elif next_next_id_loc == 0:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1
          
        values = []
        active_user = http.request.env.context.get('uid')
        id = recruitment_id
        try:
            recruitment_sudo = self._document_check_access('hr.recruitment.interviews', next_next_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
         
 
        values = self._recruitment_get_page_view_values(recruitment_sudo,next_id, pre_id, access_token, **kw) 
        return request.render("de_recruitment_portal.portal_my_recruitment", values)
 
   
    @http.route(['/recruitment/pre/<int:recruitment_id>'], type='http', auth="user", website=True)
    def portal_my_pre_recruitment(self, recruitment_id, access_token=None, **kw):
         
        recruitment_id_list = paging(0,1,0)
        pre_pre_id = 0
        recruitment_id_list.sort()
        length_list = len(recruitment_id_list)
     
        if length_list == 0:
            return request.redirect('/my')
         
        length_list = length_list - 1
        if recruitment_id in recruitment_id_list:
            recruitment_id_loc = recruitment_id_list.index(recruitment_id)
            pre_pre_id = recruitment_id_list[recruitment_id_loc - 1] 
            pre_pre_id_loc = recruitment_id_list.index(recruitment_id)
 
            if recruitment_id_loc == 1:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in recruitment_id_list:
                if ids < recruitment_id:
                    buffer_smaller = ids
                if ids > recruitment_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_smaller:
                pre_pre_id = buffer_smaller
            elif buffer_larger:
                pre_pre_id = buffer_larger
                 
            pre_pre_id_loc = recruitment_id_list.index(pre_pre_id)
            length_list = len(recruitment_id_list)
            length_list = length_list -1
            if pre_pre_id_loc == 0:
                next_id = 1
                pre_id = 0
            elif pre_pre_id_loc == length_list:
                next_id = 0
                pre_id = 1
            else:
                next_id = 1
                pre_id = 1
    
        values = []
 
        id = pre_pre_id
        try:
            recruitment_sudo = self._document_check_access('hr.recruitment.interviews', pre_pre_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
         
        recruitment_user_flag = 0
 
 
        values = self._recruitment_get_page_view_values(recruitment_sudo, next_id,pre_id, access_token, **kw) 
        return request.render("de_recruitment_portal.portal_my_recruitment", values)
