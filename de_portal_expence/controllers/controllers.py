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

def expense_page_content(flag = 0):
    managers = request.env['res.users'].search([])
    employees = request.env['hr.employee'].search([])

    return {
        'managers': managers,
        'employees' : employees,
        'success_flag' : flag,
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
        
class CreateApproval(http.Controller):
    @http.route('/expense/create/',type="http", website=True, auth='user')
    def approvals_create_template(self, **kw):
        return request.render("de_portal_expence.create_expense",expense_page_content()) 
    
    @http.route('/my/expense/save', type="http", auth="public", website=True)
    def create_expenses(self, **kw):
        expense_val = {
            'name': kw.get('expense_name'),
            'employee_id': int(kw.get('emp')),
            'user_id': int(kw.get('manager')),
#             'date_start':'date_start',
#             'date_end': 'date_end',
        }
        record = request.env['hr.expense.sheet'].sudo().create(expense_val)

        success_flag = 1
        return request.render("de_portal_expence.create_expense", expense_page_content(success_flag))

# class ActionApproval(CustomerPortal):
        
#     @http.route(['/expense/accept/<int:expense_id>'], type='http', auth="public", website=True)
#     def accept_approval(self,expense_id ,**kw):
#         id=expense_id
#         recrd = request.env['hr.expense.sheet'].sudo().browse(id)
#         recrd.action_approve()
#         approvals_page = CustomerPortal()
#         return approvals_page.portal_my_expenses()
        
#     @http.route(['/expense/reject/<int:expense_id>'], type='http', auth="public", website=True)
#     def reject_approval(self,expense_id ,**kw):
#         id=expense_id
#         recrd = request.env['hr.expense.sheet'].sudo().browse(id)
#         recrd.action_refuse()
#         approvals_page = CustomerPortal()
#         return approvals_page.portal_my_expenses()   
        
#     @http.route(['/app/rjct/<int:expense_id>'], type='http', auth="public", website=True)
#     def reject_rjct(self,expense_id , access_token=None, **kw):
#         id=expense_id
#         record = request.env['hr.expense.sheet'].sudo().browse(id)
# #         if record.request_status != 'approved': 
# #             record.action_refuse()
#         record.action_refuse()
#         try:
#             expense_sudo = self._document_check_access('hr.expense.sheet', id, access_token)
#         except (AccessError, MissingError):
#             return request.redirect('/my')
#         values = self._expense_get_page_view_values(expense_sudo, **kw) 
#         return request.render("de_portal_expence.portal_my_expense", values)
        
        
#     @http.route(['/app/ccpt/<int:expense_id>'], type='http', auth="public", website=True)
#     def reject_ccpt(self,expense_id , access_token=None, **kw):
#         id=expense_id
#         recrd = request.env['hr.expense.sheet'].sudo().browse(id)
# #         if recrd.request_status != 'refused': 
# #             recrd.action_approve()
#         recrd.action_approve()
#         try:
#             expense_sudo = self._document_check_access('hr.expense.sheet', id, access_token)
#         except (AccessError, MissingError):
#             return request.redirect('/my')
        
#         values = self._expense_get_page_view_values(expense_sudo, **kw) 
#         return request.render("de_portal_expense.portal_my_expense", values)

class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'expense_count' in counters:
            values['expense_count'] = request.env['hr.expense.sheet'].search_count([])
        return values
  
    def _expense_get_page_view_values(self,expense, next_id = 0,pre_id= 0, expense_user_flag = 0, access_token = None, **kwargs):
        values = {
            'page_name' : 'expense',
            'expense' : expense,
            'expense_user_flag': expense_user_flag,
            'next_id' : next_id,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(expense, access_token, values, 'my_expenses_history', False, **kwargs)

    @http.route(['/my/expenses', '/my/expenses/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_expenses(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'id': {'label': _('Default'), 'order': 'id asc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft', 'submit','approve','post','done','cancel'])]},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'submit': {'label': _('Submitted'), 'domain': [('state', '=', 'submit')]},  
            'approve': {'label': _('Approved'), 'domain': [('state', '=', 'approve')]},
            'post': {'label': _('Posted'), 'domain': [('state', '=', 'post')]}, 
            'done': {'label': _('Paid'), 'domain': [('state', '=', 'done')]},
            'cancel': {'label': _('Refused'), 'domain': [('state', '=', 'cancel')]},
        }
           
        searchbar_inputs = {
            'id': {'input': 'id', 'label': _('Search in No#')},
            'name': {'input': 'name', 'label': _('Search in Name')},
            'employee_id.name': {'input': 'employee_id.name', 'label': _('Search in Employee')}, 
            'user_id.name': {'input': 'user_id.name', 'label': _('Search in Manager')},
            'payment_mode': {'input': 'payment_mode', 'label': _('Search in Payment By')},
            'accounting_date': {'input': 'accounting_date', 'label': _('Search in Accounting Date')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

        expense_groups = request.env['hr.expense.sheet'].search([])

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
            if search_in in ('user_id.name', 'all'):
                search_domain = OR([search_domain, [('user_id.name', 'ilike', search)]])
            if search_in in ('payment_mode', 'all'):
                search_domain = OR([search_domain, [('payment_mode', 'ilike', search)]])
            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain
 
        expense_count = request.env['hr.expense.sheet'].search_count(domain)

        pager = portal_pager(
            url="/my/expenses",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'seissuesarch_in': search_in, 'search': search},
            total=expense_count,
            page=page,
            step=self._items_per_page
        )

        _expenses = request.env['hr.expense.sheet'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_expenses_history'] = _expenses.ids[:100]

        grouped_expenses = [_expenses]
                
        paging(0,0,1)

        paging(grouped_expenses)
        
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_expenses': grouped_expenses,
            'page_name': 'expense',
            'default_url': '/my/expenses',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        })
        return request.render("de_portal_expence.portal_my_expenses", values)

   
    @http.route(['/my/expense/<int:expense_id>'], type='http', auth="user", website=True)
    def portal_my_expense(self, expense_id, access_token=None, **kw):
        values = []
        active_user = http.request.env.context.get('uid')
        expense_user = []
        id = expense_id
        try:
            expense_sudo = self._document_check_access('hr.expense.sheet', expense_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
#         record = request.env['hr.expense.sheet'].sudo().browse(id)
#         for aprover in record.expense_ids:
#             expense_user.append(aprover.user_id.id)
        expense_user_flag = 0
#         for user in  expense_user:
#             if user == active_user:
#                 expense_user_flag = 1
                
        expense_id_list = paging(0,1,0)
        next_id = 0
        pre_id = 0
        next_next_id = 0
        expense_id_list.sort()
        length_list = len(expense_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if expense_id in expense_id_list:
                expense_id_loc = expense_id_list.index(expense_id)
                if expense_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif expense_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0
            

        values = self._expense_get_page_view_values(expense_sudo,next_id, pre_id, expense_user_flag,access_token, **kw) 
        return request.render("de_portal_expence.portal_my_expense", values)

    @http.route(['/expense/next/<int:expense_id>'], type='http', auth="user", website=True)
    def portal_my_next_expense(self, expense_id, access_token=None, **kw):
        
        expense_id_list = paging(0,1,0)
        next_next_id = 0
        expense_id_list.sort()
        
        length_list = len(expense_id_list)
        if length_list == 0:
            return request.redirect('/my')
        length_list = length_list - 1
        
        if expense_id in expense_id_list:
            expense_id_loc = expense_id_list.index(expense_id)
            next_next_id = expense_id_list[expense_id_loc + 1] 
            next_next_id_loc = expense_id_list.index(next_next_id)
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
            for ids in expense_id_list:
                if ids < expense_id:
                    buffer_smaller = ids
                if ids > expense_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_larger:
                next_next_id = buffer_smaller
            elif buffer_smaller:
                next_next_id = buffer_larger
                
            next_next_id_loc = expense_id_list.index(next_next_id)
            length_list = len(expense_id_list)
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
        id = expense_id
        try:
            expense_sudo = self._document_check_access('hr.expense.sheet', next_next_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
#         record = request.env['hr.expense.sheet'].sudo().browse(id)
#         for aprover in record.expense_ids:
#             expense_user.append(aprover.user_id.id)
        expense_user_flag = 0
#         for user in  expense_user:
#             if user == active_user:
#                 expense_user_flag = 1

        values = self._expense_get_page_view_values(expense_sudo,next_id, pre_id, access_token, **kw) 
        return request.render("de_portal_expence.portal_my_expense", values)

  
    @http.route(['/expense/pre/<int:expense_id>'], type='http', auth="user", website=True)
    def portal_my_pre_expense(self, expense_id, access_token=None, **kw):
        
        expense_id_list = paging(0,1,0)
        pre_pre_id = 0
        expense_id_list.sort()
        length_list = len(expense_id_list)
    
        if length_list == 0:
            return request.redirect('/my')
        
        length_list = length_list - 1
        if expense_id in expense_id_list:
            expense_id_loc = expense_id_list.index(expense_id)
            pre_pre_id = expense_id_list[expense_id_loc - 1] 
            pre_pre_id_loc = expense_id_list.index(expense_id)

            if expense_id_loc == 1:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in expense_id_list:
                if ids < expense_id:
                    buffer_smaller = ids
                if ids > expense_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_smaller:
                pre_pre_id = buffer_smaller
            elif buffer_larger:
                pre_pre_id = buffer_larger
                
            pre_pre_id_loc = expense_id_list.index(pre_pre_id)
            length_list = len(expense_id_list)
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
            expense_sudo = self._document_check_access('hr.expense.sheet', pre_pre_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
#         record = request.env['hr.expense.sheet'].sudo().browse(id)
#         for aprover in record.expense_ids:
#             expense_user.append(aprover.user_id.id)
        expense_user_flag = 0
#         for user in  expense_user:
#             if user == active_user:
#                 expense_user_flag = 1

        values = self._expense_get_page_view_values(expense_sudo, next_id,pre_id, access_token, **kw) 
        return request.render("de_portal_expence.portal_my_expense", values)
