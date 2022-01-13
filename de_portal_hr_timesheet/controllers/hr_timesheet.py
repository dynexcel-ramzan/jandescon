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
import ast


def timesheet_page_content(flag = 0):
    employees = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
    projects = request.env['project.project'].sudo().search([('company_id','=',employees.company_id.id)])
    tasks = request.env['project.task'].sudo().search([('company_id','=',employees.company_id.id)])
    company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    managers = employees.line_manager
    employee_name = employees
    return {
        'tasks' : tasks,
        'employees' : employees,
        'employee_name': employee_name,
        'managers': managers,
        'projects': projects,
        'success_flag' : flag,
        'company_info' : company_info
    }
   
def timesheet_page_exception( e):  
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
 
    
        
class CreateTimesheet(http.Controller):

    @http.route('/timesheet/create/',type="http", website=True, auth='user')
    def timesheet_create_template(self, **kw):
        return request.render("de_portal_hr_timesheet.hrtimesheet_template",timesheet_page_content()) 
    
    @http.route('/hr/timesheet/save',type="http", website=True, auth='user')
    def timesheet_save_template(self, **kw):
        check_in1 = kw.get('check_in').replace('T',' ')
        check_in = datetime.strptime(str(check_in1) , '%Y-%m-%d %H:%M') - relativedelta(hours =+ 5)
        timesheet_vals = {
            'employee_id': int(kw.get('employee_id')) if kw.get('employee_id') else False,
            'check_in':  check_in if check_in else False,
        }
        hr_timesheet_header = request.env['hr.timesheet.attendance'].sudo().create(timesheet_vals)
        timehseet_vals = ast.literal_eval(kw.get('timehseet_vals'))
        obj_count = 0
        for obj_line in timehseet_vals:
            obj_count += 1
            if obj_count > 1 :
                lineproject = request.env['project.project'].sudo().search([('company_id','=',hr_timesheet_header.employee_id.company_id.id),('name','=',obj_line['col1'])])
                linetask = request.env['project.task'].sudo().search([('company_id','=',hr_timesheet_header.employee_id.company_id.id),('name','=',obj_line['col2'])])
                linevals = {
                        'timesheet_att_id': hr_timesheet_header.id,
                        'project_id': lineproject.id,
                        'task_id': linetask.id,
                        'description':  obj_line['col3'],
                        'duration': obj_line['col4'], 
                }
                request.env['hr.timesheet.attendance.line'].sudo().create(linevals)
        hr_timesheet_header.action_submit()        
        return request.render("de_portal_hr_timesheet.timesheet_submited", {}, timesheet_page_content())
    
    
    
    
class CustomerPortal(CustomerPortal):
    
    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'hrtimesheet_count' in counters:
            values['hrtimesheet_count'] = request.env['hr.timesheet.attendance'].search_count([('employee_id.user_id', '=', http.request.env.context.get('uid') )])
        return values
  
    def _hrtimesheet_get_page_view_values(self,hrtimesheet, next_id = 0,pre_id= 0, hrtimesheet_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values = {
            'page_name': 'hrtimesheet',
            'hrtimesheet': hrtimesheet,
            'hrtimesheet_user_flag':hrtimesheet_user_flag,
            'next_id' : next_id,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(hrtimesheet, access_token, values, 'my_hrtimesheet_history', False, **kwargs)
    

    @http.route(['/hr/timesheets', '/hr/timesheet/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_hrtimesheets(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby=None, **kw):
        
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'employee_id': {'label': _('Employee'), 'order': 'employee_id desc' },
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

        hrtimesheet_groups = request.env['hr.timesheet.attendance'].search([])

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
        hrtimesheet_count = request.env['hr.timesheet.attendance'].search_count(domain)

        # pager
        pager = portal_pager(
            url="/hr/timesheets",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=hrtimesheet_count,
            page=page,
            step=self._items_per_page
        )

        _hrtimesheet = request.env['hr.timesheet.attendance'].sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_hrtimesheet_history'] = _hrtimesheet.ids[:100]

        grouped_hrtimesheets = [_hrtimesheet]
                
        paging(0,0,1)
        paging(grouped_hrtimesheets)
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_hrtimesheets': grouped_hrtimesheets,
            'page_name': 'hrtimesheets',
            'default_url': '/hr/timesheets',
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
        return request.render("de_portal_hr_timesheet.portal_my_hrtimesheets", values)   

   
    @http.route(['/hr/timesheet/<int:hrtimesheet_id>'], type='http', auth="user", website=True)
    def portal_my_hrtimesheet(self, hrtimesheet_id, access_token=None, **kw):

        try:
            hrtimesheet_sudo = request.env['hr.timesheet.attendance'].sudo().search([('id','=',hrtimesheet_id)])
        except (AccessError, MissingError):
            return request.redirect('/my')
        next_id = 0
        pre_id = 0
        hrtimesheet_user_flag = 0

                
        hrtimesheet_id_list = paging(0,1,0)
        next_next_id = 0
        hrtimesheet_id_list.sort()
        length_list = len(hrtimesheet_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if hrtimesheet_id in hrtimesheet_id_list:
                hrtimesheet_id_loc = hrtimesheet_id_list.index(hrtimesheet_id)
                if hrtimesheet_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif hrtimesheet_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0



        values = self._hrtimesheet_get_page_view_values(hrtimesheet_sudo,next_id, pre_id,access_token, **kw) 
        return request.render("de_portal_hr_timesheet.portal_my_hrtimesheet", values)

    @http.route(['/hrtimesheet/next/<int:hrtimesheet_id>'], type='http', auth="user", website=True)
    def portal_my_next_hrtimesheet(self, hrtimesheet_id, access_token=None, **kw):
        
        hrtimesheet_id_list = paging(0,1,0)
        next_next_id = 0
        hrtimesheet_id_list.sort()
        
        length_list = len(hrtimesheet_id_list)
        if length_list == 0:
            return request.redirect('/my')
        length_list = length_list - 1
        
        if hrtimesheet_id in hrtimesheet_id_list:
            hrtimesheet_id_loc = hrtimesheet_id_list.index(hrtimesheet_id)
            next_next_id = hrtimesheet_id_list[hrtimesheet_id_loc + 1] 
            next_next_id_loc = hrtimesheet_id_list.index(next_next_id)
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
            for ids in hrtimesheet_id_list:
                if ids < hrtimesheet_id:
                    buffer_smaller = ids
                if ids > hrtimesheet_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_larger:
                next_next_id = buffer_smaller
            elif buffer_smaller:
                next_next_id = buffer_larger
                
            next_next_id_loc = hrtimesheet_id_list.index(next_next_id)
            length_list = len(hrtimesheet_id_list)
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
        id = hrtimesheet_id
        try:
            hrtimesheet_sudo = request.env['hr.timesheet.attendance'].sudo().search([('id','=',hrtimesheet_id)])
        except (AccessError, MissingError):
            return request.redirect('/my')
        

        values = self._hrtimesheet_get_page_view_values(hrtimesheet_sudo,next_id, pre_id, access_token, **kw) 
        return request.render("de_portal_hr_timesheet.portal_my_hrtimesheet", values)

  
    @http.route(['/hrtimesheet/pre/<int:hrtimesheet_id>'], type='http', auth="user", website=True)
    def portal_my_pre_hrtimesheet(self, hrtimesheet_id, access_token=None, **kw):
        
        hrtimesheet_id_list = paging(0,1,0)
        pre_pre_id = 0
        hrtimesheet_id_list.sort()
        length_list = len(hrtimesheet_id_list)
    
        if length_list == 0:
            return request.redirect('/my')
        
        length_list = length_list - 1
        if hrtimesheet_id in hrtimesheet_id_list:
            hrtimesheet_id_loc = hrtimesheet_id_list.index(hrtimesheet_id)
            pre_pre_id = hrtimesheet_id_list[hrtimesheet_id_loc - 1] 
            pre_pre_id_loc = hrtimesheet_id_list.index(hrtimesheet_id)

            if hrtimesheet_id_loc == 1:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in hrtimesheet_id_list:
                if ids < hrtimesheet_id:
                    buffer_smaller = ids
                if ids > hrtimesheet_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_smaller:
                pre_pre_id = buffer_smaller
            elif buffer_larger:
                pre_pre_id = buffer_larger
                
            pre_pre_id_loc = hrtimesheet_id_list.index(pre_pre_id)
            length_list = len(hrtimesheet_id_list)
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
            hrtimesheet_sudo = request.env['hr.timesheet.attendance'].sudo().search([('id','=',hrtimesheet_id)])
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        hrtimesheet_user_flag = 0


        values = self._hrtimesheet_get_page_view_values(hrtimesheet_sudo, next_id,pre_id, access_token, **kw) 
        return request.render("de_portal_hr_timesheet.portal_my_hrtimesheet", values)
