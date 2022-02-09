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

def get_loan_request(flag = 0):
    employees = request.env['hr.employee'].search([('user_id','=',http.request.env.context.get('uid'))])
    loan_types = request.env['hr.loan.type'].search([])
    company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    return {
        'employees' : employees,
        'success_flag' : flag,
        'company_info': company_info,
        'loan_types': loan_types,
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
        
class CreateLoanRequest(http.Controller):
    @http.route('/loan/request/create/',type="http", website=True, auth='user')
    def action_loan_request(self, **kw):
        return request.render("de_portal_loan_request.create_loan_request",get_loan_request()) 
    
    @http.route('/loan/request/save', type="http", auth="public", website=True)
    def action_create_loan_request(self, **kw):
        expense_val = {
            'employee_id': int(kw.get('employee_id')),
            'loan_amount': kw.get('loan_amount'),
            'payment_date':  fields.date.today(),
            'loan_type_id':  int(kw.get('loan_type_id')),
            'installment':  kw.get('installment'),
        }
        record = request.env['hr.loan'].sudo().create(expense_val)
        return request.render("de_portal_loan_request.loan_request_submited", {})
    
    
    @http.route('/hr/loan/edit', type="http", auth="public", website=True)
    def edit_loan(self, **kw):
        edit_record = request.env['hr.loan'].search([('id','=',int(kw.get('id')))])
        edit_loan_val = {
                'payment_date':  fields.date.today(),
        }
        edit_record.update(edit_loan_val)
        return request.render("de_portal_expence.update_loan_request_submited", {})
        
    
        

class CustomerPortal(CustomerPortal):
    
   
    
    
    @http.route(['/loan/installment/compute/list/<int:loan_id>'], type='http', auth="public", website=True)
    def compute_loan_nstallment_list(self,loan_id ,**kw):
        id=loan_id
        recrd = request.env['hr.loan'].sudo().browse(id)
        recrd.compute_installment()
        loan_page = CustomerPortal()
        return loan_page.portal_loan_request()
    

    @http.route(['/loan/installment/compute/<int:loan_id>'], type='http', auth="public", website=True)
    def compute_loan_nstallment(self,loan_id , access_token=None, **kw):
        id=loan_id
        record = request.env['hr.loan'].sudo().browse(id)
        record.compute_installment()
        try:
            loan_sudo = self._document_check_access('hr.loan', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._loan_request_get_page_view_values(loan_sudo, **kw) 
        return request.render("de_portal_loan_request.portal_loan_request_form", values)
    
    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'loan_count' in counters:
            values['loan_count'] = request.env['hr.loan'].search_count([('employee_id.user_id', '=', http.request.env.context.get('uid') )])
        return values
  
    def _loan_request_get_page_view_values(self,loan, next_id = 0,pre_id= 0, loan_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])

        values = {
            'page_name' : 'loan',
            'loan' : loan,
            'loan_user_flag': loan_user_flag,
            'company_info': company_info,
            'next_id' : next_id,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(loan, access_token, values, 'loan_history', False, **kwargs)

    @http.route(['/loan/request', '/loan/request/page/<int:page>'], type='http', auth="user", website=True)
    def portal_loan_request(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'id': {'label': _('Default'), 'order': 'id asc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Reason'), 'order': 'name desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {  
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft', 'waiting_approval_1','waiting_approval_2','approve','cancel'])]},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'waiting_approval_1': {'label': _('Submitted'), 'domain': [('state', '=', 'waiting_approval_1')]},  
            'waiting_approval_2': {'label': _('Waiting Approval'), 'domain': [('state', '=', 'waiting_approval_2')]},
            'approve': {'label': _('Approved'), 'domain': [('state', '=', 'approve')]}, 
            'cancel': {'label': _('Cancel'), 'domain': [('state', '=', 'cancel')]},
        }
           
        searchbar_inputs = {
            'id': {'input': 'id', 'label': _('Search in Sequence')},
            'name': {'input': 'name', 'label': _('Search in Name')},
            'employee_id.name': {'input': 'employee_id.name', 'label': _('Search in Employee')}, 
            'loan_amount': {'input': 'loan_amount', 'label': _('Search in Amount')},
            'date': {'input': 'date', 'label': _('Search in Date')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

        loan_groups = request.env['hr.loan'].search([])

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
            if search_in in ('loan_amount', 'all'):
                search_domain = OR([search_domain, [('loan_amount', 'ilike', search)]])
            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain
 
        loan_count = request.env['hr.loan'].search_count(domain)

        pager = portal_pager(
            url="/loan/request",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'seissuesarch_in': search_in, 'search': search},
            total=loan_count,
            page=page,
            step=self._items_per_page
        )

        loan_request = request.env['hr.loan'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['loan_history'] = loan_request.ids[:100]

        grouped_loan_request = [loan_request]
                
        paging(0,0,1)

        paging(grouped_loan_request)
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_loan_request': grouped_loan_request,
            'page_name': 'Loan Request',
            'default_url': '/loan/request',
            'company_info': company_info,
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            
        })
        return request.render("de_portal_loan_request.portal_loan_request", values)

   
    @http.route(['/loan/request/form/<int:loan_id>'], type='http', auth="user", website=True)
    def portal_loan_request_form(self, loan_id, access_token=None, **kw):
        values = []
        active_user = http.request.env.context.get('uid')
        expense_user = []
        id = loan_id
        try:
            loan_sudo = self._document_check_access('hr.loan', loan_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')        

        loan_request_user_flag = 0
                
        loan_id_list = paging(0,1,0)
        next_id = 0
        pre_id = 0
        next_next_id = 0
        loan_id_list.sort()
        length_list = len(loan_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if loan_id in loan_id_list:
                loan_id_loc = loan_id_list.index(loan_id)
                if loan_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif loan_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0
            

        values = self._loan_request_get_page_view_values(loan_sudo,next_id, pre_id, loan_request_user_flag,access_token, **kw) 
        return request.render("de_portal_loan_request.portal_loan_request_form", values)

    @http.route(['/loan/request/next/<int:loan_id>'], type='http', auth="user", website=True)
    def portal_next_loan_request(self, loan_id, access_token=None, **kw):
        
        loan_id_list = paging(0,1,0)
        next_next_id = 0
        loan_id_list.sort()
        
        length_list = len(loan_id_list)
        if length_list == 0:
            return request.redirect('/my')
        length_list = length_list - 1
        
        if loan_id in loan_id_list:
            loan_id_loc = loan_id_list.index(loan_id)
            next_next_id = loan_id_list[loan_id_loc + 1] 
            next_next_id_loc = loan_id_list.index(next_next_id)
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
            for ids in loan_id_list:
                if ids < loan_id:
                    buffer_smaller = ids
                if ids > loan_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_larger:
                next_next_id = buffer_smaller
            elif buffer_smaller:
                next_next_id = buffer_larger
                
            next_next_id_loc = loan_id_list.index(next_next_id)
            length_list = len(loan_id_list)
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
        id = loan_id
        try:
            loan_sudo = self._document_check_access('hr.loan', next_next_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        expense_user_flag = 0


        values = self._loan_request_get_page_view_values(loan_sudo,next_id, pre_id, access_token, **kw) 
        return request.render("de_portal_loan_request.portal_loan_request_form", values)

  
    @http.route(['/loan/request/previous/<int:loan_id>'], type='http', auth="user", website=True)
    def portal_previous_loan_request(self, loan_id, access_token=None, **kw):
        
        loan_id_list = paging(0,1,0)
        pre_pre_id = 0
        loan_id_list.sort()
        length_list = len(loan_id_list)
    
        if length_list == 0:
            return request.redirect('/my')
        
        length_list = length_list - 1
        if loan_id in loan_id_list:
            loan_id_loc = loan_id_list.index(loan_id)
            pre_pre_id = loan_id_list[loan_id_loc - 1] 
            pre_pre_id_loc = loan_id_list.index(loan_id)

            if loan_id_loc == 1:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in loan_id_list:
                if ids < loan_id:
                    buffer_smaller = ids
                if ids > loan_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_smaller:
                pre_pre_id = buffer_smaller
            elif buffer_larger:
                pre_pre_id = buffer_larger
                
            pre_pre_id_loc = loan_id_list.index(pre_pre_id)
            length_list = len(loan_id_list)
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
            loan_sudo = self._document_check_access('hr.loan', pre_pre_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        expense_user_flag = 0
        
        values = self._loan_request_get_page_view_values(loan_sudo, next_id,pre_id, access_token, **kw) 
        return request.render("de_portal_loan_request.portal_loan_request_form", values)
