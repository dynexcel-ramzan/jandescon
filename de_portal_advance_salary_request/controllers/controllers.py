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




# def approval_page_content(flag = 0):
#     partner = request.env['res.partner'].search([])
#     category = request.env['approval.category'].search([])

#     return {
#         'approval_data': category,
#         'oweners_res_partner' : partner,
#         'success_flag' : flag
#     }
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
 
# class CreateApproval(http.Controller):

#     @http.route('/approval/create/',type="http", website=True, auth='user')
#     def approvals_create_template(self, **kw):
#         return request.render("de_portal_advance_salary_request.create_approval",approval_page_content()) 
    
#     @http.route('/my/approval/save', type="http", auth="public", website=True)
#     def create_approvals(self, **kw):
#         approval_val = {
#             'name': kw.get('approval_name'),
#             'has_location': kw.get('approval_has_loc'),
#             'category_id': int(kw.get('approval_category_id')),
# #             'date_start':'date_start',
# #             'date_end': 'date_end',
#         }
#         record = request.env['approval.request'].sudo().create(approval_val)

#         success_flag = 1
#         return request.render("de_portal_advance_salary_request.create_approval", approval_page_content(success_flag))

# class ActionApproval(CustomerPortal):
        
#     @http.route(['/approval/accept/<int:approval_id>'], type='http', auth="public", website=True)
#     def accept_approval(self,approval_id ,**kw):
#         id=approval_id
#         recrd = request.env['approval.request'].sudo().browse(id)
#         recrd.action_approve()
#         approvals_page = CustomerPortal()
#         return approvals_page.portal_my_salaries()
        
#     @http.route(['/approval/reject/<int:approval_id>'], type='http', auth="public", website=True)
#     def reject_approval(self,approval_id ,**kw):
#         id=approval_id
#         recrd = request.env['approval.request'].sudo().browse(id)
#         recrd.action_refuse()
#         approvals_page = CustomerPortal()
#         return approvals_page.portal_my_salaries()   
        
#     @http.route(['/app/rjct/<int:approval_id>'], type='http', auth="public", website=True)
#     def reject_rjct(self,approval_id , access_token=None, **kw):
#         id=approval_id
#         record = request.env['approval.request'].sudo().browse(id)
# #         if record.request_status != 'approved': 
# #             record.action_refuse()
#         record.action_refuse()
#         try:
#             salary_sudo = self._document_check_access('approval.request', id, access_token)
#         except (AccessError, MissingError):
#             return request.redirect('/my')
#         values = self._salaries_get_page_view_values(salary_sudo, **kw) 
#         return request.render("de_portal_advance_salary_request.portal_my_salary", values)
        
        
#     @http.route(['/app/ccpt/<int:approval_id>'], type='http', auth="public", website=True)
#     def reject_ccpt(self,approval_id , access_token=None, **kw):
#         id=approval_id
#         recrd = request.env['approval.request'].sudo().browse(id)
# #         if recrd.request_status != 'refused': 
# #             recrd.action_approve()
#         recrd.action_approve()
#         try:
#             salary_sudo = self._document_check_access('approval.request', id, access_token)
#         except (AccessError, MissingError):
#             return request.redirect('/my')
        
#         values = self._salaries_get_page_view_values(salary_sudo, **kw) 
#         return request.render("de_portal_advance_salary_request.portal_my_salary", values)


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'salary_count' in counters:
            values['salary_count'] = request.env['hr.employee.advance.salary'].search_count([])
        return values
  
    
    def _salaries_get_page_view_values(self, salary,next_id = 0, pre_id = 0, salary_user_flag = 0,access_token = None, **kwargs):
        values = {
            'page_name': 'salary',
            'salary': salary,
            'salary_user_flag':salary_user_flag,
            'next_id' : next_id,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(salary, access_token, values, 'my_salaries_history', False, **kwargs)
    

    @http.route(['/my/salaries', '/my/salaries/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_salaries(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'id': {'label': _('Default'), 'order': 'id asc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft', 'request','approval','hrconfirm','paid','close'])]},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'request': {'label': _('Approval'), 'domain': [('state', '=', 'request')]},  
            'approval': {'label': _('HR Confirm'), 'domain': [('state', '=', 'approval')]},
            'hrconfirm': {'label': _('Paid'), 'domain': [('state', '=', 'hrconfirm')]}, 
            'paid': {'label': _('Close'), 'domain': [('state', '=', 'paid')]},
            'close': {'label': _('Cancel'), 'domain': [('state', '=', 'close')]},
        }
   
        
        searchbar_inputs = {
            'id': {'input': 'id', 'label': _('Search in No#')},
            'name': {'input': 'name', 'label': _('Search in Reference')},
#             'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
#             'reason': {'input': 'reason', 'label': _('Search in Description')},
            
            'employee_id.name': {'input': 'employee_id.name', 'label': _('Search in Employee')},
            'manager_id.name': {'input': 'manager_id.name', 'label': _('Search in Manager ')},
#             'partner_id.name': {'input': 'partner_id.name', 'label': _('Search in Contact')},
#             'request_status': {'input': 'request_status', 'label': _('Search in Stages')},
#             'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

        project_groups = request.env['hr.employee.advance.salary'].search([])

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
            if search_in in ('reason', 'all'):
                search_domain = OR([search_domain, [('reason', 'ilike', search)]])
            if search_in in ('employee_id.name', 'all'):
                search_domain = OR([search_domain, [('employee_id.name', 'ilike', search)]])
            if search_in in ('manager_id.name', 'all'):
                search_domain = OR([search_domain, [('manager_id.name', 'ilike', search)]])
#             if search_in in ('partner_id.name', 'all'):
#                 search_domain = OR([search_domain, [('partner_id.name', 'ilike', search)]])
#             if search_in in ('request_status', 'all'):
#                 search_domain = OR([search_domain, [('request_status', 'ilike', search)]])
            domain += search_domain
 
        salary_count = request.env['hr.employee.advance.salary'].search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/salaries",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'seissuesarch_in': search_in, 'search': search},
            total=salary_count,
            page=page,
            step=self._items_per_page
        )

        _salaries = request.env['hr.employee.advance.salary'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_salaries_history'] = _salaries.ids[:100]

        grouped_salaries = [_salaries]
       
        paging(0,0,1)

        paging(grouped_salaries)
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_salaries': grouped_salaries,
            'page_name': 'salary',
            'default_url': '/my/salaries',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        })
        return request.render("de_portal_advance_salary_request.portal_my_salaries", values)   

    @http.route(['/my/salary/<int:salary_id>'], type='http', auth="user", website=True)
    def portal_my_salary(self, salary_id, access_token=None, **kw):
        values = []
        active_user = http.request.env.context.get('uid')

        id = salary_id
        try:
            salary_sudo = self._document_check_access('hr.employee.advance.salary', salary_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        salary_user_flag = 1
#         raise UserError((salary_user_flag))

        next_id = 0
        pre_id = 0
        salary_user_flag = 0
                
        salary_id_list = paging(0,1,0)
        next_next_id = 0
        salary_id_list.sort()
        length_list = len(salary_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if salary_id in salary_id_list:
                salary_id_loc = salary_id_list.index(salary_id)
                if salary_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif salary_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0

        values = self._salaries_get_page_view_values(salary_sudo, next_id, pre_id, salary_user_flag,access_token, **kw) 
        return request.render("de_portal_advance_salary_request.portal_my_salary", values)

#     hr.employee.advance.salary

    @http.route(['/salary/next/<int:salary_id>'], type='http', auth="user", website=True)
    def portal_my_salary_next(self, salary_id, access_token=None, **kw):
                
        salary_id_list = paging(0,1,0)
        next_id = 0
        pre_id = 0
        salary_user_flag = 0
        next_next_id = 0
        salary_id_list.sort()
        
        length_list = len(salary_id_list)
        if length_list == 0:
            return request.redirect('/my')
        length_list = length_list - 1
        
        if salary_id in salary_id_list:
            salary_id_loc = salary_id_list.index(salary_id)
            next_next_id = salary_id_list[salary_id_loc + 1] 
            next_next_id_loc = salary_id_list.index(next_next_id)
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
            for ids in salary_id_list:
                if ids < salary_id:
                    buffer_smaller = ids
                if ids > salary_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_larger:
                next_next_id = buffer_smaller
            elif buffer_smaller:
                next_next_id = buffer_larger
                
            next_next_id_loc = salary_id_list.index(next_next_id)
            length_list = len(salary_id_list)
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
        try:
            salary_sudo = self._document_check_access('hr.employee.advance.salary', next_next_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        values = self._salaries_get_page_view_values(salary_sudo,next_id, pre_id, access_token, **kw) 
        return request.render("de_portal_advance_salary_request.portal_my_salary", values)

    @http.route(['/salary/pre/<int:salary_id>'], type='http', auth="user", website=True)
    def portal_my_salary_pre(self, salary_id, access_token=None, **kw):
              
        salary_id_list = paging(0,1,0)
        pre_pre_id = 0
        next_id = 0
        pre_id = 0
        salary_id_list.sort()
        
        length_list = len(salary_id_list)
        
        
        
        if length_list == 0:
            return request.redirect('/my')
        length_list = length_list - 1
        

        if salary_id in salary_id_list:
            salary_id_loc = salary_id_list.index(salary_id)
            pre_pre_id = salary_id_list[salary_id_loc - 1] 
            pre_pre_id_loc = salary_id_list.index(salary_id)
            if pre_pre_id_loc == 1:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1     
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in salary_id_list:
                if ids < salary_id:
                    buffer_smaller = ids
                if ids > salary_id:
                    buffer_larger = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_smaller:
                pre_pre_id = buffer_smaller
            elif buffer_larger:
                pre_pre_id = buffer_larger
                
            pre_pre_id_loc = salary_id_list.index(pre_pre_id)
            length_list = len(salary_id_list)
            length_list = length_list - 1
            if pre_pre_id_loc == 0:
                next_id = 1
                pre_id = 0
            elif pre_pre_id_loc == length_list:
                next_id = 0
                pre_id = 1
            else:
                next_id = 1
                pre_id = 1

        try:
            salary_sudo = self._document_check_access('hr.employee.advance.salary', pre_pre_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        values = self._salaries_get_page_view_values(salary_sudo,next_id, pre_id, access_token, **kw) 
        return request.render("de_portal_advance_salary_request.portal_my_salary", values)

    