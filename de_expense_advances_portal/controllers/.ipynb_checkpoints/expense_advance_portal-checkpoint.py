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


def action_check_expense_warning(warning):
    company_info = request.env['res.users'].sudo().search([('id', '=', http.request.env.context.get('uid'))])
    return {
        'warning_message': warning,
        'company_info': company_info
    }

def expense_adv_page_content(flag = 0):
    employees = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
    company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    categories = request.env['ora.expense.category'].sudo().search([])
    date = fields.date.today()
    return {
        'employees' : employees,
        'categories': categories,
        'date': date.strftime('%d/%b/%Y'),
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
 
    
        
class CreateExpenseAdvances(http.Controller):
    @http.route('/expense/advance/create/',type="http", website=True, auth='user')
    def create_expense_advances(self, **kw):
        return request.render("de_expense_advances_portal.expense_adv_template",expense_adv_page_content()) 
    
    @http.route('/my/expense/advance/save', type="http", auth="public", website=True)
    def expense_adv_submit_forms(self, **kw):
        employee = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
        matching_date = fields.date.today() - timedelta(365)
        expense_advances = request.env['advance.against.expense'].sudo().search([('employee_id','=',employee.id),('date','>=', matching_date)])
        expense_count = 0
        for expense in expense_advances:
            if expense.state=='waiting':
                expense_count += 1
            if expense.state=='approved':
                pass
        
        if expense_count >= 2:
            warning_message = 'You are not allow to Submit Document your already two unadjusted payment Pending! Please contact with Accounting Department.'
            return request.render("de_portal_expence.expense_submited_validation", action_check_expense_warning(warning_message)) 
        if int(kw.get('employee_id')):
            employee_id = request.env['hr.employee'].search([('id','=',int(kw.get('employee_id')))], order="id desc", limit=1)
            
            if kw.get('description'):
                request_val = {
                    'employee_id': int(kw.get('employee_id')),            
                    'date':fields.date.today(),
                    'amount': float(kw.get('amount')),
                    'description': kw.get('description'),
                }
                record = request.env['advance.against.expense'].sudo().create(request_val)
                record.send_for_approval()
                
        return request.render("de_expense_advances_portal.request_submitted", {}, expense_adv_page_content())
  

    
    
    
class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'expense_adv_count' in counters:
            values['expense_adv_count'] = request.env['advance.against.expense'].search_count([])
        return values
  
    def _expense_adv_get_page_view_values(self,expense_adv, next_id = 0,pre_id= 0, expense_adv_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values = {
            'page_name': 'Expense Advances',
            'expense_adv': expense_adv,
            'expense_adv_user_flag':expense_adv_user_flag,
            'next_id' : next_id,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(expense_adv, access_token, values, 'my_expense_adv_history', False, **kwargs)
    

    @http.route(['/my/expense/advances', '/my/expense/advances/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_expense_advs(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby=None, **kw):
        
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'employee_id': {'label': _('Employee'), 'order': 'employee_id desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft', 'waiting','approved', 'reject'])]},
            'draft': {'label': _('To Submit'), 'domain': [('state', '=', 'draft')]},
            'waiting': {'label': _('Waiting Approval'), 'domain': [('state', '=', 'waiting')]},  
            'approved': {'label': _('Approved'), 'domain': [('state', '=', 'approved')]},
            'reject': {'label': _('Rejected'), 'domain': [('state', '=', 'reject')]}, 
        }
                                 
        searchbar_inputs = {  
            'name': {'input': 'name', 'label': _('Search in Employee')},
            'id': {'input': 'id', 'label': _('Search in Ref#')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }
        employee = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
        expense_adv_groups = request.env['advance.against.expense'].sudo().search([('employee_id','=',employee.id)])

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
            domain +=  [('employee_id','=',employee.id)]
        expense_adv_count = request.env['advance.against.expense'].search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/expense/advances",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'seissuesarch_in': search_in, 'search': search},
            total=555,
            page=page,
            step=self._items_per_page
        )

        _expense_adv = request.env['advance.against.expense'].sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_expense_adv_history'] = _expense_adv.ids[:100]

        grouped_expense_adva = [_expense_adv]
        grouped_expense_adv = request.env['advance.against.expense'].sudo().search([('employee_id','=',employee.id)])        
        paging(0,0,1)
        paging(grouped_expense_adv)
        company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_expense_adv': grouped_expense_adv,
            'page_name': 'Expense Advances',
            'default_url': '/my/expense/advances',
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
        return request.render("de_expense_advances_portal.portal_my_expense_advs", values)   

   
    @http.route(['/my/expense/advance/<int:resignation_id>'], type='http', auth="user", website=True)
    def portal_my_expense_adv(self, resignation_id, access_token=None, **kw):
        try:
            expense_adv_sudo = self._document_check_access('advance.against.expense', resignation_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        next_id = 0
        pre_id = 0
        expense_adv_user_flag = 0
                 
        resignation_id_list = paging(0,1,0)
        next_next_id = 0
        resignation_id_list.sort()
        length_list = len(resignation_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if resignation_id in resignation_id_list:
                resignation_id_loc = resignation_id_list.index(resignation_id)
                if resignation_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif resignation_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0
 
 
        values = self._expense_adv_get_page_view_values(expense_adv_sudo,next_id, pre_id,access_token, **kw) 
        return request.render("de_expense_advances_portal.portal_my_expense_adv", values)
 
    @http.route(['/expense/advance/next/<int:expense_adv_id>'], type='http', auth="user", website=True)
    def portal_my_next_advance_exp(self, expense_adv_id, access_token=None, **kw):
         
        expense_adv_id_list = paging(0,1,0)
        next_next_id = 0
        expense_adv_id_list.sort()
         
        length_list = len(expense_adv_id_list)
        if length_list == 0:
            return request.redirect('/my')
        length_list = length_list - 1
         
        if expense_adv_id in expense_adv_id_list:
            expense_adv_id_loc = expense_adv_id_list.index(expense_adv_id)
            next_next_id = expense_adv_id_list[expense_adv_id_loc + 1] 
            next_next_id_loc = expense_adv_id_list.index(next_next_id)
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
            for ids in expense_adv_list:
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
                 
            next_next_id_loc = expense_adv_id_list.index(next_next_id)
            length_list = len(expense_adv_id_list)
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
        id = expense_adv_id
        try:
            expense_adv_sudo = self._document_check_access('advance.against.expense', next_next_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
         
 
        values = self._expense_adv_get_page_view_values(expense_adv_sudo,next_id, pre_id, access_token, **kw) 
        return request.render("de_expense_advances_portal.portal_my_expense_adv", values)
 
   
    @http.route(['/expense/advance/pre/<int:expense_adv_id>'], type='http', auth="user", website=True)
    def portal_my_pre_advance_exp(self, expense_adv_id, access_token=None, **kw):
         
        expense_adv_id_list = paging(0,1,0)
        pre_pre_id = 0
        expense_adv_id_list.sort()
        length_list = len(expense_adv_id_list)
     
        if length_list == 0:
            return request.redirect('/my')
         
        length_list = length_list - 1
        if expense_adv_id in expense_adv_id_list:
            expense_adv_id_loc = expense_adv_id_list.index(expense_adv_id)
            pre_pre_id = expense_adv_id_list[expense_adv_id_loc - 1] 
            pre_pre_id_loc = expense_adv_id_list.index(expense_adv_id)
 
            if expense_adv_id_loc == 1:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in expense_adv_id_list:
                if ids < expense_adv_id:
                    buffer_smaller = ids
                if ids > expense_adv_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_smaller:
                pre_pre_id = buffer_smaller
            elif buffer_larger:
                pre_pre_id = buffer_larger
                 
            pre_pre_id_loc = expense_adv_id_list.index(pre_pre_id)
            length_list = len(expense_adv_id_list)
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
            expense_adv_sudo = self._document_check_access('advance.against.expense', pre_pre_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
         
        expense_adv_user_flag = 0
 
 
        values = self._expense_adv_get_page_view_values(expense_adv_sudo, next_id,pre_id, access_token, **kw) 
        return request.render("de_expense_advances_portal.portal_my_expense_adv", values)
