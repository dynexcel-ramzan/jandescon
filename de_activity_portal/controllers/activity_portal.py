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

def activity_page_content(flag = 0):
    users = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    activity_types = request.env['mail.activity.type'].search([])
    return {
        'users' : users,
        'activity_types': activity_types,
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
 
    
        
class CreateActivity(http.Controller):

    @http.route('/activity/create/',type="http", website=True, auth='user')
    def activity_create_template(self, **kw):
        return request.render("de_activity_portal.activity_template",activity_page_content()) 
    
    @http.route('/my/activity/save', type="http", auth="public", website=True)
    def activity_submit_forms(self, **kw):
        if kw.get('description'):
            activity_val = {
                'employee_id': int(kw.get('employee_id')),            
                'activity_type':kw.get('activity_type'),
                'activity_reason': kw.get('activity_reason'),
                'expected_revealing_date': kw.get('last_day_of_employee'),
                'reason':kw.get('description'),
            }
            record = request.env['mail.activity'].sudo().create(activity_val)
            
        return request.render("de_activity_portal.activity_submitted", {}, activity_page_content())
  

    
    
    
class CustomerPortal(CustomerPortal):

    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'activity_count' in counters:
            values['activity_count'] = request.env['mail.activity'].search_count([('user_id', '=', http.request.env.context.get('uid') )])
            print('========================', values['activity_count'])
        return values
  
    def _activity_get_page_view_values(self,activity, next_id = 0,pre_id= 0, activity_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values = {
            'page_name': 'activity',
            'activity': activity,
            'activity_user_flag':activity_user_flag,
            'next_id' : next_id,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(activity, access_token, values, 'my_activity_history', False, **kwargs)
    

    @http.route(['/my/activities', '/my/activities/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_activities(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby=None, **kw):
        
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'employee_id': {'label': _('Employee'), 'order': 'employee_id desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft', 'cancel','confirm','approved'])]},
            
            'draft': {'label': _('To Submit'), 'domain': [('state', '=', 'draft')]},
            'cancel': {'label': _('Cancelled'), 'domain': [('state', '=', 'cancel')]},  
            'confirm': {'label': _('Confirmed'), 'domain': [('state', '=', 'confirm')]},
            'approved': {'label': _('Refused'), 'domain': [('state', '=', 'approved')]}, 
        }
                                 
        
        searchbar_inputs = {  
            'name': {'input': 'name', 'label': _('Search in Employee')},
            'id': {'input': 'id', 'label': _('Search in Ref#')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

        activity_groups = request.env['mail.activity'].search([])

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
        activity_count = request.env['mail.activity'].search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/activities",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'seissuesarch_in': search_in, 'search': search},
            total=555,
            page=page,
            step=self._items_per_page
        )

        _activity = request.env['mail.activity'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_activity_history'] = _activity.ids[:100]

        grouped_activities = [_activity]
                
        paging(0,0,1)
        paging(grouped_activities)
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_activities': grouped_activities,
            'page_name': 'activities',
            'default_url': '/my/activities',
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
        return request.render("de_activity_portal.portal_my_activities", values)   

   
    @http.route(['/my/activity/<int:activity_id>'], type='http', auth="user", website=True)
    def portal_my_activity(self, activity_id, access_token=None, **kw):
        try:
            activity_sudo = self._document_check_access('mail.activity', activity_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        next_id = 0
        pre_id = 0
        activity_user_flag = 0
                 
        activity_id_list = paging(0,1,0)
        next_next_id = 0
        activity_id_list.sort()
        length_list = len(activity_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if activity_id in activity_id_list:
                activity_id_loc = activity_id_list.index(activity_id)
                if activity_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif activity_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0
 
 
        values = self._activity_get_page_view_values(activity_sudo,next_id, pre_id,access_token, **kw) 
        return request.render("de_activity_portal.portal_my_activity", values)
    
    
    @http.route(['/activity/mark_done/<int:activity_id>'], type='http', auth="user", website=True)
    def portal_mark_done_activity(self, activity_id, access_token=None, **kw):
        print('===========portal_mark_done_activity=========',activity_id)
        record = request.env['mail.activity'].browse(activity_id)
        record.action_done()
        return request.render("de_activity_portal.mark_as_done_successfully",activity_page_content()) 

        
    
    @http.route(['/activity/next/<int:activity_id>'], type='http', auth="user", website=True)
    def portal_my_next_activity(self, activity_id, access_token=None, **kw):
         
        activity_id_list = paging(0,1,0)
        next_next_id = 0
        activity_id_list.sort()
         
        length_list = len(activity_id_list)
        if length_list == 0:
            return request.redirect('/my')
        length_list = length_list - 1
         
        if activity_id in activity_id_list:
            activity_id_loc = activity_id_list.index(activity_id)
            next_next_id = activity_id_list[activity_id_loc + 1] 
            next_next_id_loc = activity_id_list.index(next_next_id)
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
            for ids in activity_id_list:
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
                 
            next_next_id_loc = activity_id_list.index(next_next_id)
            length_list = len(activity_id_list)
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
        id = activity_id
        try:
            activity_sudo = self._document_check_access('mail.activity', next_next_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
         
 
        values = self._activity_get_page_view_values(activity_sudo,next_id, pre_id, access_token, **kw) 
        return request.render("de_activity_portal.portal_my_activity", values)
 
   
    @http.route(['/activity/pre/<int:activity_id>'], type='http', auth="user", website=True)
    def portal_my_pre_activity(self, activity_id, access_token=None, **kw):
         
        activity_id_list = paging(0,1,0)
        pre_pre_id = 0
        activity_id_list.sort()
        length_list = len(activity_id_list)
     
        if length_list == 0:
            return request.redirect('/my')
         
        length_list = length_list - 1
        if activity_id in activity_id_list:
            activity_id_loc = activity_id_list.index(activity_id)
            pre_pre_id = activity_id_list[activity_id_loc - 1] 
            pre_pre_id_loc = activity_id_list.index(activity_id)
 
            if activity_id_loc == 1:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in activity_id_list:
                if ids < activity_id:
                    buffer_smaller = ids
                if ids > activity_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_smaller:
                pre_pre_id = buffer_smaller
            elif buffer_larger:
                pre_pre_id = buffer_larger
                 
            pre_pre_id_loc = activity_id_list.index(pre_pre_id)
            length_list = len(activity_id_list)
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
            activity_sudo = self._document_check_access('mail.activity', pre_pre_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
         
        activity_user_flag = 0
 
 
        values = self._activity_get_page_view_values(activity_sudo, next_id,pre_id, access_token, **kw) 
        return request.render("de_activity_portal.portal_my_activity", values)
