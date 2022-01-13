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

def timeoff_page_content(flag = 0):
    leave_type = request.env['hr.leave.type'].search([('is_publish','=', True)])
    employees = request.env['hr.employee'].search([('user_id','=',http.request.env.context.get('uid'))])
    leave_allocation = request.env['hr.leave.allocation'].search([('employee_id.user_id', '=', http.request.env.context.get('uid') )])
    company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    return {
        'leave_type' : leave_type,
        'employees' : employees,
        'leave_allocation': leave_allocation,
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
 
    
        
class CreateTimeOff(http.Controller):

    @http.route('/timeoff/create/',type="http", website=True, auth='user')
    def timeoff_create_template(self, **kw):
        return request.render("de_leave_portal.leave_template",timeoff_page_content()) 
    
    @http.route('/my/timeoff/save', type="http", auth="public", website=True)
    def leave_submit_forms(self, **kw):
        if kw.get('leave_category_id') == 'day':
            date_start1 = datetime.strptime(kw.get('date_start') , '%Y-%m-%d')
            date_end1 =  datetime.strptime(kw.get('date_end') , '%Y-%m-%d')
            request_date_start1 = datetime.strptime(kw.get('date_start') , '%Y-%m-%d')
            request_date_end1 =  datetime.strptime(kw.get('date_end') , '%Y-%m-%d')
            date_start = date_start1 + relativedelta(hours =+ 4)  
            date_end =  date_end1 + relativedelta(hours =+ 14)
            request_date_start = request_date_start1  
            request_date_end =  request_date_end1 
            
            days = (date_start1 - date_end1).days
            
            date_weekday = datetime.strptime(kw.get('date_start') , '%Y-%m-%d')
            
            weekday = date_weekday.weekday()
            
            employee_schedule = request.env['hr.employee'].search([('id','=', int(kw.get('employee_id')))])
            for emp_schedule in employee_schedule.resource_calendar_id.attendance_ids:
                if emp_schedule.dayofweek == weekday:
                    date_start1 = datetime.strptime(kw.get('date_start') , '%Y-%m-%d')
                    date_start2 = datetime.strptime(kw.get('date_end') , '%Y-%m-%d')
                    date_start =  date_start1 + relativedelta(hours =+ emp_schedule.hours_from)       
                    date_end =  date_start2 + relativedelta(hours =+ emp_schedule.hours_to)  
                    request_date_start =  date_start1 + relativedelta(hours =+ emp_schedule.hours_from)       
                    request_date_end =  date_start2 + relativedelta(hours =+ emp_schedule.hours_to)  
            
            
            attached_files = request.httprequest.files.getlist('attachment_id')
            pdf64 = binascii.b2a_base64(kw.get('attachment_id'))
            attachment_invoice = self.env['ir.attachment'].create(
            {
             "name": 'file',
             'type': 'binary',
              "datas": pdf64
                })
                    
            timeoff_val = {
                'holiday_status_id': int(kw.get('leave_type_id')),
                'employee_id': int(kw.get('employee_id')),            
                'date_from':date_start,
                'date_to': date_end,
                'request_date_from':str(kw.get('date_start')),
                'request_date_to': str(kw.get('date_end')),
                'name':kw.get('description'),
#                 'attachment_id': [[6, 0, [attachment_invoice.id]]],
            }
            record = request.env['hr.leave'].sudo().create(timeoff_val)
            
            
        if kw.get('leave_category_id') == 'half_day':
            day_half = kw.get('leave_half_day')
            date_from = kw.get('half_day_date') 
            date_start = kw.get('half_day_date') 
            date_end =  kw.get('half_day_date') 
            
            day_period = 'am'
            if day_half == 'Morning':
                day_period = 'am'
                date_start1 = datetime.strptime(kw.get('half_day_date') , '%Y-%m-%d')
                date_start2 = datetime.strptime(kw.get('half_day_date') , '%Y-%m-%d')
                date_start = date_start1 + relativedelta(hours =+ 4)  
                date_end =  date_start2 + relativedelta(hours =+ 12)  
            elif day_half == 'Evening':
                day_period = 'pm'
                date_start1 = datetime.strptime(kw.get('half_day_date') , '%Y-%m-%d')
                date_start2 = datetime.strptime(kw.get('half_day_date') , '%Y-%m-%d')
                date_start = date_start1 + relativedelta(hours =+ 7)  
                date_end =  date_start2 + relativedelta(hours =+ 11)
            if 'attachment_id' in request.params:
                attached_files = request.httprequest.files.getlist('attachment_id')
                for attachment in attached_files:
                    attached_file = attachment.read()
                    attachment = request.env['ir.attachment'].sudo().create({
                                'name': attachment.filename,
                                'res_model': 'hr.leave',
                                'type': 'binary',
                                'datas_fname': attachment.filename,
                                'datas': attached_file.encode('base64'),
                            })    
            timeoff_val = {
                'holiday_status_id': int(kw.get('leave_type_id')),
                'employee_id': int(kw.get('employee_id')),            
                'date_from':date_start,
                'date_to': date_end,
                'request_unit_half': True,
                'request_date_from':kw.get('half_day_date'),
                'request_date_from_period': day_period,
                'name':kw.get('description'),
#                 'attachment_id': [[6, 0, [attachment.id]]],
            }
            record = request.env['hr.leave'].sudo().create(timeoff_val)   
        
        attachment = 0
        if kw.get('leave_category_id') == 'hours':
           
            attached_files = request.httprequest.files.getlist('attachment_id')
            for attachment in attached_files:
                    attached_file = attachment.read()
                    attachment = request.env['ir.attachment'].sudo().create({
                                'name': attachment.filename,
                                'res_model': 'hr.leave',
                                'type': 'binary',
                                'datas_fname': attachment.filename,
                                'datas': attached_file.encode('base64'),
                            })  
            hour_from = kw.get('time_from')            
            hour_to =  str(float(kw.get('time_from')) + 2)
            timeoff_val = {
                'holiday_status_id': int(kw.get('leave_type_id')),
                'employee_id': int(kw.get('employee_id')),            
                'date_from':kw.get('hours_date'),
                'date_to': kw.get('hours_date'),
                'request_unit_hours':True,
                'request_date_from': kw.get('hours_date'),
                'request_hour_from': hour_from ,
                'request_hour_to':  hour_to,
                'name':kw.get('description'),
#                 'attachment_id':[[6, 0, [attachment.id]]],
            }
            record = request.env['hr.leave'].sudo().create(timeoff_val)
            
        return request.render("de_leave_portal.leave_submited", {}, timeoff_page_content())
  

    
    
    
class CustomerPortal(CustomerPortal):

    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'timeoff_count' in counters:
            values['timeoff_count'] = request.env['hr.leave'].search_count([('employee_id.user_id', '=', http.request.env.context.get('uid') )])
        return values
  
    def _timeoff_get_page_view_values(self,timeoff, next_id = 0,pre_id= 0, timeoff_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values = {
            'page_name': 'timeoff',
            'timeoff': timeoff,
            'timeoff_user_flag':timeoff_user_flag,
            'next_id' : next_id,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(timeoff, access_token, values, 'my_timeoff_history', False, **kwargs)
    

    @http.route(['/my/timeoffs', '/my/timeoff/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_timeoffs(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby=None, **kw):
        
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'employee_id': {'label': _('Employee'), 'order': 'employee_id desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft', 'cancel','confirm','refuse','validate1','validate'])]},
            
            'draft': {'label': _('To Submit'), 'domain': [('state', '=', 'draft')]},
            'cancel': {'label': _('Cancelled'), 'domain': [('state', '=', 'cancel')]},  
            'confirm': {'label': _('To Approve'), 'domain': [('state', '=', 'confirm')]},
            'refuse': {'label': _('Refused'), 'domain': [('state', '=', 'refuse')]}, 
            'validate1': {'label': _('Second Approved'), 'domain': [('state', '=', 'validate1')]},
            'validate': {'label': _('Approved'), 'domain': [('state', '=', 'validate')]},
        }
                                 
        
        searchbar_inputs = {  
            'name': {'input': 'name', 'label': _('Search in Employee')},
            'id': {'input': 'id', 'label': _('Search in Ref#')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

        timeoff_groups = request.env['hr.leave'].search([])

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
        timeoff_count = request.env['hr.leave'].search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/timeoffs",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'seissuesarch_in': search_in, 'search': search},
            total=555,
            page=page,
            step=self._items_per_page
        )

        _timeoff = request.env['hr.leave'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_timeoff_history'] = _timeoff.ids[:100]

        grouped_timeoffs = [_timeoff]
                
        paging(0,0,1)
        paging(grouped_timeoffs)
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_timeoffs': grouped_timeoffs,
            'page_name': 'timeoffs',
            'default_url': '/my/timeoffs',
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
        return request.render("de_leave_portal.portal_my_timeoffs", values)   

   
    @http.route(['/my/timeoff/<int:timeoff_id>'], type='http', auth="user", website=True)
    def portal_my_timeoff(self, timeoff_id, access_token=None, **kw):

        try:
            timeoff_sudo = self._document_check_access('hr.leave', timeoff_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        next_id = 0
        pre_id = 0
        timeoff_user_flag = 0

                
        timeoff_id_list = paging(0,1,0)
        next_next_id = 0
        timeoff_id_list.sort()
        length_list = len(timeoff_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if timeoff_id in timeoff_id_list:
                timeoff_id_loc = timeoff_id_list.index(timeoff_id)
                if timeoff_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif timeoff_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0



        values = self._timeoff_get_page_view_values(timeoff_sudo,next_id, pre_id,access_token, **kw) 
        return request.render("de_leave_portal.portal_my_timeoff", values)

    @http.route(['/timeoff/next/<int:timeoff_id>'], type='http', auth="user", website=True)
    def portal_my_next_timeoff(self, timeoff_id, access_token=None, **kw):
        
        timeoff_id_list = paging(0,1,0)
        next_next_id = 0
        timeoff_id_list.sort()
        
        length_list = len(timeoff_id_list)
        if length_list == 0:
            return request.redirect('/my')
        length_list = length_list - 1
        
        if timeoff_id in timeoff_id_list:
            timeoff_id_loc = timeoff_id_list.index(timeoff_id)
            next_next_id = timeoff_id_list[timeoff_id_loc + 1] 
            next_next_id_loc = timeoff_id_list.index(next_next_id)
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
            for ids in timeoff_id_list:
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
                
            next_next_id_loc = timeoff_id_list.index(next_next_id)
            length_list = len(timeoff_id_list)
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
        id = timeoff_id
        try:
            timeoff_sudo = self._document_check_access('hr.leave', next_next_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        

        values = self._timeoff_get_page_view_values(timeoff_sudo,next_id, pre_id, access_token, **kw) 
        return request.render("de_leave_portal.portal_my_timeoff", values)

  
    @http.route(['/timeoff/pre/<int:timeoff_id>'], type='http', auth="user", website=True)
    def portal_my_pre_timeoff(self, timeoff_id, access_token=None, **kw):
        
        timeoff_id_list = paging(0,1,0)
        pre_pre_id = 0
        timeoff_id_list.sort()
        length_list = len(timeoff_id_list)
    
        if length_list == 0:
            return request.redirect('/my')
        
        length_list = length_list - 1
        if timeoff_id in timeoff_id_list:
            timeoff_id_loc = timeoff_id_list.index(timeoff_id)
            pre_pre_id = timeoff_id_list[timeoff_id_loc - 1] 
            pre_pre_id_loc = timeoff_id_list.index(timeoff_id)

            if timeoff_id_loc == 1:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in timeoff_id_list:
                if ids < timeoff_id:
                    buffer_smaller = ids
                if ids > timeoff_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_smaller:
                pre_pre_id = buffer_smaller
            elif buffer_larger:
                pre_pre_id = buffer_larger
                
            pre_pre_id_loc = timeoff_id_list.index(pre_pre_id)
            length_list = len(timeoff_id_list)
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
            timeoff_sudo = self._document_check_access('hr.leave', pre_pre_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        timeoff_user_flag = 0


        values = self._timeoff_get_page_view_values(timeoff_sudo, next_id,pre_id, access_token, **kw) 
        return request.render("de_leave_portal.portal_my_timeoff", values)
