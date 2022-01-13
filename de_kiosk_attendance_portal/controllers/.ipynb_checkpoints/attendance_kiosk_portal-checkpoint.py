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

def kattendance_page_content(flag = 0):
    employees = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
    company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
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
 
    
        
class CreateKAttendance(http.Controller):

    @http.route('/kattendance/create/checkin',type="http", website=True, auth='user')
    def kattendance_create_checkin(self, **kw):
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        kinemployee = request.env['hr.employee'].sudo().search([('user_id','=', http.request.env.context.get('uid'))])
        
        att_exists = request.env['hr.attendance.wfh'].sudo().search([('employee_id','=', kinemployee.id),('check_out','=',False),('date','=', fields.date.today()),('reason','=','WFH(Work From Home)')], order='check_in desc', limit=1)
        if att_exists:
            print(att_exists.check_in)
            return request.render("de_kiosk_attendance_portal.already_checkin_exists",kattendance_page_content()) 
        
        else: 
            att_val = {
                'employee_id': kinemployee.id,
                'date': fields.date.today(),
                'reason': 'WFH(Work From Home)',
                'check_in': current_datetime,
            }
            record = request.env['hr.attendance.wfh'].sudo().create(att_val)
            return request.render("de_kiosk_attendance_portal.kattendance_checkin_template",kattendance_page_content()) 
    
    @http.route('/kattendance/create/checkout',type="http", website=True, auth='user')
    def kattendance_create_checkout(self, **kw):
        print('datetime.now()',datetime.now())
        print('datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")',datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        koutemployee = request.env['hr.employee'].sudo().search([('user_id','=', http.request.env.context.get('uid'))])
        att_date =  fields.date.today()
        att_exists = request.env['hr.attendance.wfh'].sudo().search([('employee_id','=', koutemployee.id),('check_out','=',False),('date','=',att_date),('reason','=','WFH(Work From Home)')], order="check_in asc" , limit=1)
        
        if att_exists:
            att_val = {
                'check_out':current_datetime,
                'reason': 'WFH(Work From Home)', 
            }
            record = att_exists.sudo().write(att_val)
            att_exists.action_submit()
            return request.render("de_kiosk_attendance_portal.kattendance_checkin_template",kattendance_page_content()) 
        else:
            return request.render("de_kiosk_attendance_portal.no_checkin_exists",kattendance_page_content()) 

    
    
 
    
class CustomerPortal(CustomerPortal):

    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'kattendance_count' in counters:
            values['kattendance_count'] = request.env['hr.attendance.wfh'].sudo().search_count([('employee_id.user_id', '=', http.request.env.context.get('uid') )])
        return values
  
    def _resignation_get_page_view_values(self,kattendance, next_id = 0,pre_id= 0, kattendance_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
        values = {
            'page_name': 'kisok attendance',
            'kattendance': kattendance,
            'kattendance_user_flag':kattendance_user_flag,
            'next_id' : next_id,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(kattendance, access_token, values, 'my_timeoff_history', False, **kwargs)
    

    @http.route(['/my/kattendance', '/my/kattendance/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_kattendances(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby=None, **kw):
        print('----------------in py method')
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

        kemployee = request.env['hr.employee'].sudo().search([('user_id','=', http.request.env.context.get('uid'))])
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
            
        domain += [('employee_id', '=', kemployee.id)]
        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            domain += search_domain
        kattendance_count = request.env['hr.attendance.wfh'].sudo().search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/kattendance",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'seissuesarch_in': search_in, 'search': search},
            total=555,
            page=page,
            step=self._items_per_page
        )

        _kattendance = request.env['hr.attendance.wfh'].sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_timeoff_history'] = _kattendance.ids[:100]

        grouped_kattendances = [_kattendance]
        grouped_check_in = True
        grouped_check_out = False
                
        paging(0,0,1)
        paging(grouped_kattendances)
        company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_kattendances': grouped_kattendances,
            'grouped_check_in': grouped_check_in,
            'grouped_check_out': grouped_check_out,
            'page_name': 'Kiosk Attendance',
            'default_url': '/my/kattendance',
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
        return request.render("de_kiosk_attendance_portal.portal_my_kattendances", values)   

   

