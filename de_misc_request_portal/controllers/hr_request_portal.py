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

def request_page_content(flag = 0):
    employees = request.env['hr.employee'].search([('user_id','=',http.request.env.context.get('uid'))])
    company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    request_types = request.env['hr.request.config'].search([('company_id','=',request.env.company.id)])
    return {
        'employees' : employees,
        'request_types': request_types,
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
 
    
        
class CreateRequest(http.Controller):

    @http.route('/request/create/',type="http", website=True, auth='user')
    def request_create_template(self, **kw):
        return request.render("de_misc_request_portal.request_template",request_page_content()) 
    
    @http.route('/my/request/save', type="http", auth="public", website=True)
    def request_submit_forms(self, **kw):
        if kw.get('description'):
            request_val = {
                'employee_id': int(kw.get('employee_id')),            
                'request_type_id':int(kw.get('request_type_id')),
                'description': kw.get('description'),
                'best_before_date': kw.get('best_before_date'),
            }
            record = request.env['hr.request'].sudo().create(request_val)
            record.action_submit()
            
        return request.render("de_misc_request_portal.request_submitted", {}, request_page_content())
  

    
    
    
class CustomerPortal(CustomerPortal):

    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'request_count' in counters:
            values['request_count'] = request.env['hr.request'].search_count([('employee_id.user_id', '=', http.request.env.context.get('uid') )])
        return values
  
    def _request_get_page_view_values(self,request_id, next_id = 0,pre_id= 0, request_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        print('1111111request_id',request_id)
        values = {
            'page_name': 'request',
            'request_id': request_id,
            'request_user_flag':request_user_flag,
            'next_id' : next_id,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(request_id, access_token, values, 'my_request_history', False, **kwargs)
    

    @http.route(['/my/misc/requests', '/my/misc/requests/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_requests(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby=None, **kw):
        
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'best_before_date desc'},
            'employee_id': {'label': _('Employee'), 'order': 'employee_id desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft', 'refused','submitted','approved'])]},
            
            'draft': {'label': _('To Submit'), 'domain': [('state', '=', 'draft')]},
            'refused': {'label': _('Refused'), 'domain': [('state', '=', 'refused')]},  
            'submitted': {'label': _('Submitted'), 'domain': [('state', '=', 'submitted')]},
            'approved': {'label': _('Approved'), 'domain': [('state', '=', 'approved')]}, 
        }
                                 
        
        searchbar_inputs = {  
            'name': {'input': 'name', 'label': _('Search in Employee')},
            'id': {'input': 'id', 'label': _('Search in Ref#')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

        request_groups = request.env['hr.request'].search([])

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
        if date_begin and date_end:
            domain += [('best_before_date', '>', date_begin), ('best_before_date', '<=', date_end)]       

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            domain += search_domain
        request_count = request.env['hr.request'].search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/misc/requests",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'seissuesarch_in': search_in, 'search': search},
            total=555,
            page=page,
            step=self._items_per_page
        )

        _request = request.env['hr.request'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_request_history'] = _request.ids[:100]

        grouped_requests = [_request]
                
        paging(0,0,1)
        paging(grouped_requests)
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_requests': grouped_requests,
            'page_name': 'requests',
            'default_url': '/my/misc/requests',
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
        return request.render("de_misc_request_portal.portal_my_requests", values)   

   
    @http.route(['/my/misc/request/<int:request_id>'], type='http', auth="user", website=True)
    def portal_my_request(self, request_id, access_token=None, **kw):
        try:
            request_sudo = self._document_check_access('hr.request', request_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        print('request_sudo',request_sudo)

        next_id = 0
        pre_id = 0
        request_user_flag = 0
                 
        request_id_list = paging(0,1,0)
        next_next_id = 0
        request_id_list.sort()
        length_list = len(request_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if request_id in request_id_list:
                request_id_loc = request_id_list.index(request_id)
                if request_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif request_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0
 
 
        values = self._request_get_page_view_values(request_sudo,next_id, pre_id,access_token, **kw) 
        return request.render("de_misc_request_portal.portal_my_misc_request", values)
    
    
#     @http.route(['/request/mark_done/<int:request_id>'], type='http', auth="user", website=True)
#     def portal_mark_done_request(self, request_id, access_token=None, **kw):
#         print('===========portal_mark_done_request=========',request_id)
#         record = request.env['hr.request'].browse(request_id)
#         record.action_done()
#         return request.render("de_misc_request_portal.mark_as_done_successfully",request_page_content()) 

        
    
    @http.route(['/request/next/<int:request_id>'], type='http', auth="user", website=True)
    def portal_my_next_request(self, request_id, access_token=None, **kw):
         
        request_id_list = paging(0,1,0)
        next_next_id = 0
        request_id_list.sort()
         
        length_list = len(request_id_list)
        if length_list == 0:
            return request.redirect('/my')
        length_list = length_list - 1
         
        if request_id in request_id_list:
            request_id_loc = request_id_list.index(request_id)
            next_next_id = request_id_list[request_id_loc + 1] 
            next_next_id_loc = request_id_list.index(next_next_id)
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
            for ids in request_id_list:
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
                 
            next_next_id_loc = request_id_list.index(next_next_id)
            length_list = len(request_id_list)
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
        id = request_id
        try:
            request_sudo = self._document_check_access('hr.request', next_next_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
         
 
        values = self._request_get_page_view_values(request_sudo,next_id, pre_id, access_token, **kw) 
        return request.render("de_misc_request_portal.portal_my_misc_request", values)
 
   
    @http.route(['/request/pre/<int:request_id>'], type='http', auth="user", website=True)
    def portal_my_pre_request(self, request_id, access_token=None, **kw):
         
        request_id_list = paging(0,1,0)
        pre_pre_id = 0
        request_id_list.sort()
        length_list = len(request_id_list)
     
        if length_list == 0:
            return request.redirect('/my')
         
        length_list = length_list - 1
        if request_id in request_id_list:
            request_id_loc = request_id_list.index(request_id)
            pre_pre_id = request_id_list[request_id_loc - 1] 
            pre_pre_id_loc = request_id_list.index(request_id)
 
            if request_id_loc == 1:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in request_id_list:
                if ids < request_id:
                    buffer_smaller = ids
                if ids > request_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_smaller:
                pre_pre_id = buffer_smaller
            elif buffer_larger:
                pre_pre_id = buffer_larger
                 
            pre_pre_id_loc = request_id_list.index(pre_pre_id)
            length_list = len(request_id_list)
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
            request_sudo = self._document_check_access('hr.request', pre_pre_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
         
        request_user_flag = 0
 
 
        values = self._request_get_page_view_values(request_sudo, next_id,pre_id, access_token, **kw) 
        return request.render("de_misc_request_portal.portal_my_misc_request", values)
