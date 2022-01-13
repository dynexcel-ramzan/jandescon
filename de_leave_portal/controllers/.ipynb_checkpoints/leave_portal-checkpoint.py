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
import json



def timeoff_page_content(flag = 0):
    leave_type = request.env['hr.leave.type'].search([('is_publish','=', True)])
    employees = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
    leave_allocation = request.env['hr.leave.allocation'].sudo().search([('employee_id.user_id', '=', http.request.env.context.get('uid') )])
    
    company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    managers = employees.line_manager
    employee_name = employees
    return {
        'leave_type' : leave_type,
        'employees' : employees,
        'employee_name': employee_name,
        'managers': managers,
        'leave_allocation': leave_allocation,
        'success_flag' : flag,
        'company_info' : company_info
    }
   
def timeoff_page_exception( e):  
    return {
        'e': e
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
            
            days = (date_end1 - date_start1).days
            
            date_weekday = datetime.strptime(kw.get('date_start') , '%Y-%m-%d')
            
            weekday = date_weekday.weekday()
            hours_from = 8
            hours_to = 16
            employee_schedule = request.env['hr.employee'].search([('id','=', int(kw.get('employee_id')))])
            for emp_schedule in employee_schedule.shift_id.attendance_ids:
                hours_from = emp_schedule.hour_from
                hours_to = emp_schedule.hour_to               
                if emp_schedule.dayofweek == weekday:
                    hours_from = emp_schedule.hour_from
                    hours_to = emp_schedule.hour_to       
            
            date_start =  date_start1 + relativedelta(hours =+ hours_from) 
            date_end = date_end1 + relativedelta(hours =+ hours_to)
            
            if kw.get('attachment'):
                Attachments = request.env['ir.attachment']

                name = kw.get('attachment').filename

                file = kw.get('attachment')
                attachment_id = Attachments.sudo().create({

                'name': name,

                'type': 'binary',

                'datas': base64.b64encode(file.read()),
                 })
               
                timeoff_val = {
                    'holiday_status_id': int(kw.get('leave_type_id')),
                    'employee_id': int(kw.get('employee_id')),            
                    'date_from':date_start,
                    'date_to': date_end,
                    'leave_category': kw.get('leave_category_id'),
                    'attachment_id': [(4, attachment_id.id)],
                    'request_date_from':str(kw.get('date_start')),
                    'request_date_to': str(kw.get('date_end')),
                    'name':kw.get('description'),
                }
                record = request.env['hr.leave'].sudo().create(timeoff_val)
            else:
                timeoff_val = {
                    'holiday_status_id': int(kw.get('leave_type_id')),
                    'employee_id': int(kw.get('employee_id')),            
                    'date_from':date_start,
                    'date_to': date_end,
                    'leave_category': kw.get('leave_category_id'),
                    'request_date_from':str(kw.get('date_start')),
                    'request_date_to': str(kw.get('date_end')),
                    'name':kw.get('description'),
                }
                record = request.env['hr.leave'].sudo().create(timeoff_val)
                
                
            if kw.get('date_start') and kw.get('date_end'):
                dddate_from = datetime.strptime(str(kw.get('date_start')), '%Y-%m-%d')
                dddate_to = datetime.strptime(str(kw.get('date_end')), '%Y-%m-%d')
                dddelta = dddate_to - dddate_from
                shift_schedule_line = request.env['hr.shift.schedule.line'].sudo().search([('employee_id','=',int(kw.get('employee_id'))),('date','>=',str(kw.get('date_start'))),('date','<=',str(kw.get('date_end')))])
                tot_rest_days = 0
                gazetted_days_count = 0
                COUNT_1 = 0
                for shift_line in shift_schedule_line:
                    shift = shift_line.first_shift_id
                    if not shift:
                        shift = employee_schedule.shift_id
                    if not shift:
                        shift = request.env['resource.calendar'].sudo().search([('company_id','=',employee_schedule.company_id.id)], limit=1)
                    
                    for gazetted_day in shift.global_leave_ids:
                        gazetted_date_from = gazetted_day.date_from +timedelta(1)
                        gazetted_date_to = gazetted_day.date_to
                        if str(shift_line.date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(shift_line.date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                            raise UserError(str(shift_line.date)+' g '+str(gazetted_date_from))
                            gazetted_days_count += 1 
                                                
                    if shift_line.rest_day == True:
                        for gazetted_day in shift.global_leave_ids:
                            gazetted_date_from = gazetted_day.date_from +timedelta(1)
                            gazetted_date_to = gazetted_day.date_to
                            if str(shift_line.date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(shift_line.date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                                gazetted_days_count += 1 
                                tot_rest_days -= 1    
                                
                        tot_rest_days += 1    
                    
                   
                if dddelta.days == 0.0:
                    record.update({
                    'number_of_days': 1
                    })
                else:
                    raise UserError(str(tot_rest_days)+' g '+str(gazetted_days_count))
                    total_days = dddelta.days + 1 - tot_rest_days - gazetted_days_count
                    record.update({
                      'number_of_days': total_days
                    })    

            

            
        if kw.get('leave_category_id') == 'half_day':
            day_half = kw.get('leave_half_day')
            date_from = kw.get('half_day_date') 
            date_start = kw.get('half_day_date') 
            date_end =  kw.get('half_day_date') 

            date_weekday = datetime.strptime(kw.get('half_day_date') , '%Y-%m-%d')
            
            weekday = date_weekday.weekday()
            employee11 = request.env['hr.employee'].search([('id','=', int(kw.get('employee_id')))], limit=1)
            hour_to =  str((employee11.shift_id.hours_per_day/2))
            date_start1 = datetime.strptime(kw.get('half_day_date') , '%Y-%m-%d')
            date_start2 = datetime.strptime(kw.get('half_day_date') , '%Y-%m-%d')
            hours_from = 8
            hours_to = 16
            employee_schedule = request.env['hr.employee'].search([('id','=', int(kw.get('employee_id')))])
            for emp_schedule in employee_schedule.shift_id.attendance_ids:
                hours_from = emp_schedule.hour_from
                hours_to = emp_schedule.hour_to               
                if emp_schedule.dayofweek == weekday:
                    hours_from = emp_schedule.hour_from
                    hours_to = emp_schedule.hour_to
                    
            date_start =  date_start1 + relativedelta(hours =+ hours_from) 
            date_end = date_start2 + relativedelta(hours =+ hours_to)  
            
            day_period = 'am'
            if day_half == 'Morning':
                day_period = 'am'
                date_end = date_end - relativedelta(hours =+ float(employee_schedule.shift_id.hours_per_day)/2)     
                
            elif day_half == 'Evening':
                day_period = 'pm'
                date_start =  date_start + relativedelta(hours =+ float(employee_schedule.shift_id.hours_per_day)/2) 
           
            
            leave_period_half = 'first_half'
            request_date_from_period = 'am'
            if day_half == 'Evening':
                leave_period_half = 'second_half' 
                request_date_from_period = 'pm'
                
            timeoff_val = {
                'holiday_status_id': int(kw.get('leave_type_id')),
                'employee_id': int(kw.get('employee_id')),            
                'date_from':date_start - relativedelta(hours =+ 5),
                'date_to': date_end - relativedelta(hours =+ 5),
                'leave_period_half': leave_period_half,  
                'request_unit_half': True,
                'request_date_from_period': request_date_from_period,
                'leave_category': kw.get('leave_category_id'),
                'leave_category': kw.get('leave_category_id'),
                'request_date_from':kw.get('half_day_date'),
                'request_date_to': kw.get('half_day_date'),
                'number_of_days': 0.50 ,
                'name':kw.get('description'),
            }
            record = request.env['hr.leave'].sudo().create(timeoff_val)
            record.update({
                'number_of_days': 0.50,
                'date_from':date_start - relativedelta(hours =+ 5),
                'date_to': date_end - relativedelta(hours =+ 5),
            })
            record.update({
                'number_of_days': 0.50,

            })
            if kw.get('attachment'):
                Attachments = request.env['ir.attachment']
                name = kw.get('attachment').filename
                file = kw.get('attachment')
                attachment_id = Attachments.create({
                'name': name,
                'type': 'binary',
                'datas': base64.b64encode(file.read()),
                 })
                record.update({
                   'attachment_id': [(4, attachment_id.id)],
                 })
        
        attachment = 0
        if kw.get('leave_category_id') == 'hours':
           
             
            hour_from = kw.get('time_from') 
            employee11 = request.env['hr.employee'].search([('id','=', int(kw.get('employee_id')))], limit=1)
            hour_to =  str(float(kw.get('time_from').replace(":",".")) + (employee11.shift_id.hours_per_day/4))
            date_start1 = datetime.strptime(kw.get('hours_date') , '%Y-%m-%d')
            short_leave_start_obj = datetime.strptime(kw.get('time_from'), '%H:%M')
            date_start =  date_start1 + relativedelta(hours =+ short_leave_start_obj.hour,minutes=short_leave_start_obj.minute)       
            date_end =  date_start + relativedelta(hours =+ float(employee11.shift_id.hours_per_day/4))
            timeoff_val = {
                'holiday_status_id': int(kw.get('leave_type_id')),
                'employee_id': int(kw.get('employee_id')),            
                'date_from':date_start,
                'short_start_time': kw.get('time_from').replace(":","."),
                'date_to': date_end,
                'leave_category': kw.get('leave_category_id'),
                'request_date_from':kw.get('hours_date'),
                'request_date_to': kw.get('hours_date'),
                'number_of_days': 0.25 ,
                'name':kw.get('description'),
            }
            record = request.env['hr.leave'].sudo().create(timeoff_val)
            record.update({
                'number_of_days': 0.25 ,
                'date_from':date_start - relativedelta(hours =+ 5),
                'date_to': date_end - relativedelta(hours =+ 5),
            })
            record.update({
                'number_of_days': 0.25 ,

            })
            if kw.get('attachment'):
                Attachments = request.env['ir.attachment']

                name = kw.get('attachment').filename

                file = kw.get('attachment')
                attachment_id = Attachments.create({

                'name': name,

                'type': 'binary',

                'datas': base64.b64encode(file.read()),
                })
                record.update({
                   'attachment_id': [(4, attachment_id.id)],
                 })

        return request.render("de_leave_portal.leave_submited", {}, timeoff_page_content())
  

    
    
    
class CustomerPortal(CustomerPortal):
    
    @http.route(['/hr/leave/cancel/<int:approval_id>'], type='http', auth="public", website=True)
    def approval_reject(self,approval_id ,**kw):
        id=approval_id
        recrd = request.env['hr.leave'].sudo().browse(id)
        recrd.action_cancel()
        approvals_page = CustomerPortal()
        return request.render("de_leave_portal.leave_cancel", {})
    
    


    

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
        domain += [('employee_id.user_id', '=', http.request.env.context.get('uid'))] 
        timeoff_count = request.env['hr.leave'].search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/timeoffs",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=timeoff_count,
            page=page,
            step=self._items_per_page
        )

        _timeoff = request.env['hr.leave'].sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
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
