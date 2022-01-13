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
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR

def get_advance_salary(flag = 0):
    employees = request.env['hr.employee'].search([('user_id','=',http.request.env.context.get('uid'))])
    company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    return {
        'employees' : employees,
        'success_flag' : flag,
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
        
class CreateAdvanceSalary(http.Controller):
    @http.route('/advance/salary/create/',type="http", website=True, auth='user')
    def action_advance_salary(self, **kw):
        return request.render("de_portal_advance_salary_request.create_advance_salary",get_advance_salary()) 
    
    @http.route('/advance/salary/save', type="http", auth="public", website=True)
    def action_create_advance_salary(self, **kw):
        expense_val = {
            'reason': kw.get('description'),
            'employee_id': int(kw.get('employee_id')),
            'advance': kw.get('advance_amount'),
            'date':  fields.date.today(),
        }
        record = request.env['salary.advance'].sudo().create(expense_val)
        return request.render("de_portal_advance_salary_request.advance_salary_submited", {})
        

class CustomerPortal(CustomerPortal):
    

    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'advance_count' in counters:
            values['advance_count'] = request.env['salary.advance'].search_count([('employee_id.user_id', '=', http.request.env.context.get('uid') )])
        return values
  
    def _advance_salary_get_page_view_values(self,advance, next_id = 0,pre_id= 0, advance_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values = {
            'page_name' : 'advance',
            'advance' : advance,
            'advance_user_flag': advance_user_flag,
            'next_id' : next_id,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(advance, access_token, values, 'advance_salary_history', False, **kwargs)

    @http.route(['/advance/salary', '/advance/salary/page/<int:page>'], type='http', auth="user", website=True)
    def portal_advance_salary(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'id': {'label': _('Default'), 'order': 'id asc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Reason'), 'order': 'reason desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft', 'submit','waiting_approval','approve','cancel','reject'])]},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'submit': {'label': _('Submitted'), 'domain': [('state', '=', 'submit')]},  
            'waiting_approval': {'label': _('Waiting Approval'), 'domain': [('state', '=', 'waiting_approval')]},
            'approve': {'label': _('Approved'), 'domain': [('state', '=', 'approve')]}, 
            'cancel': {'label': _('Cancel'), 'domain': [('state', '=', 'cancel')]},
            'reject': {'label': _('Reject'), 'domain': [('state', '=', 'reject')]},
        }
           
        searchbar_inputs = {
            'id': {'input': 'id', 'label': _('Search in Sequence')},
            'reason': {'input': 'reason', 'label': _('Search in Reason')},
            'employee_id.name': {'input': 'employee_id.name', 'label': _('Search in Employee')}, 
            'advance': {'input': 'advance', 'label': _('Search in Amount')},
            'date': {'input': 'date', 'label': _('Search in Date')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

        expense_groups = request.env['salary.advance'].search([])

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
            if search_in in ('employee_id.name', 'all'):
                search_domain = OR([search_domain, [('employee_id.name', 'ilike', search)]])
            if search_in in ('advance', 'all'):
                search_domain = OR([search_domain, [('advance', 'ilike', search)]])
            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain
 
        expense_count = request.env['salary.advance'].search_count(domain)

        pager = portal_pager(
            url="/advance/salary",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'seissuesarch_in': search_in, 'search': search},
            total=expense_count,
            page=page,
            step=self._items_per_page
        )

        adv_salary = request.env['salary.advance'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['advance_salary_history'] = adv_salary.ids[:100]

        grouped_adv_salary = [adv_salary]
                
        paging(0,0,1)

        paging(grouped_adv_salary)
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_adv_salary': grouped_adv_salary,
            'page_name': 'Advance Salary',
            'default_url': '/advance/salary',
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
        return request.render("de_portal_advance_salary_request.portal_advance_salary", values)

   
    @http.route(['/advance/salary/<int:advance_id>'], type='http', auth="user", website=True)
    def portal_advance_salary_request(self, advance_id, access_token=None, **kw):
        values = []
        active_user = http.request.env.context.get('uid')
        expense_user = []
        id = advance_id
        try:
            advance_sudo = self._document_check_access('salary.advance', advance_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')        

        adv_salary_user_flag = 0
                
        advance_id_list = paging(0,1,0)
        next_id = 0
        pre_id = 0
        next_next_id = 0
        advance_id_list.sort()
        length_list = len(advance_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if advance_id in advance_id_list:
                advance_id_loc = advance_id_list.index(advance_id)
                if advance_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif advance_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0
            

        values = self._advance_salary_get_page_view_values(advance_sudo,next_id, pre_id, adv_salary_user_flag,access_token, **kw) 
        return request.render("de_portal_advance_salary_request.portal_advance_salary_request", values)

    @http.route(['/advance/salary/next/<int:advance_id>'], type='http', auth="user", website=True)
    def portal_my_next_expense(self, advance_id, access_token=None, **kw):
        
        advance_id_list = paging(0,1,0)
        next_next_id = 0
        advance_id_list.sort()
        
        length_list = len(advance_id_list)
        if length_list == 0:
            return request.redirect('/my')
        length_list = length_list - 1
        
        if advance_id in advance_id_list:
            advance_id_loc = advance_id_list.index(advance_id)
            next_next_id = advance_id_list[advance_id_loc + 1] 
            next_next_id_loc = advance_id_list.index(next_next_id)
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
            for ids in advance_id_list:
                if ids < advance_id:
                    buffer_smaller = ids
                if ids > advance_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_larger:
                next_next_id = buffer_smaller
            elif buffer_smaller:
                next_next_id = buffer_larger
                
            next_next_id_loc = advance_id_list.index(next_next_id)
            length_list = len(advance_id_list)
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
        expense_user = []
        id = advance_id
        try:
            advance_sudo = self._document_check_access('salary.advance', next_next_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        expense_user_flag = 0


        values = self._advance_salary_get_page_view_values(advance_sudo,next_id, pre_id, access_token, **kw) 
        return request.render("de_portal_advance_salary_request.portal_advance_salary_request", values)

  
    @http.route(['/advance/salary/previous/<int:advance_id>'], type='http', auth="user", website=True)
    def portal_previous_advance_salary(self, advance_id, access_token=None, **kw):
        
        advance_id_list = paging(0,1,0)
        pre_pre_id = 0
        advance_id_list.sort()
        length_list = len(advance_id_list)
    
        if length_list == 0:
            return request.redirect('/my')
        
        length_list = length_list - 1
        if advance_id in advance_id_list:
            advance_id_loc = advance_id_list.index(advance_id)
            pre_pre_id = advance_id_list[advance_id_loc - 1] 
            pre_pre_id_loc = advance_id_list.index(advance_id)

            if advance_id_loc == 1:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in advance_id_list:
                if ids < advance_id:
                    buffer_smaller = ids
                if ids > advance_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_smaller:
                pre_pre_id = buffer_smaller
            elif buffer_larger:
                pre_pre_id = buffer_larger
                
            pre_pre_id_loc = advance_id_list.index(pre_pre_id)
            length_list = len(advance_id_list)
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
        active_user = http.request.env.context.get('uid')
        expense_user = []
        id = pre_pre_id
        try:
            advance_sudo = self._document_check_access('salary.advance', pre_pre_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        expense_user_flag = 0
        
        values = self._advance_salary_get_page_view_values(advance_sudo, next_id,pre_id, access_token, **kw) 
        return request.render("de_portal_advance_salary_request.portal_advance_salary_request", values)
