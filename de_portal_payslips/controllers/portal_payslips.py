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

def payslip_page_content(flag = 0):
    emps = request.env['hr.employee'].search([])
    structure = request.env['hr.payroll.structure'].search([])

    return {
        'emps': emps,
        'structure' : structure,
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
        
class CreatePayslip(http.Controller):
    @http.route('/payslip/create/',type="http", website=True, auth='user')
    def payslips_create_template(self, **kw):
        return request.render("de_portal_payslips.create_payslip",payslip_page_content()) 
    
    @http.route('/my/payslip/save', type="http", auth="public", website=True)
    def create_payslips(self, **kw):
        payslip_val = {
            'name': kw.get('payslip_name'),
            'number': kw.get('payslip_number'),
            'employee_id': int(kw.get('payslip_emp_id')),
            'struct_id': int(kw.get('payslip_structure_id')),
            'date_from':kw.get('date_start'),
            'date_to': kw.get('date_end'),
        }
        record = request.env['hr.payslip'].sudo().create(payslip_val)

        success_flag = 1
        return request.render("de_portal_payslips.create_payslip", payslip_page_content(success_flag))



class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'payslip_count' in counters:
            values['payslip_count'] = request.env['hr.payslip'].search_count([])
        return values
  
    def _payslips_get_page_view_values(self,payslip, next_id = 0,pre_id= 0, payslip_user_flag = 0, access_token = None, **kwargs):
        values = {
            'page_name' : 'payslip',
            'payslip' : payslip,
            'payslip_user_flag': payslip_user_flag,
            'next_id' : next_id,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(payslip, access_token, values, 'my_payslip_history', False, **kwargs)

    @http.route(['/my/payslips', '/my/payslips/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_payslips(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'id': {'label': _('Default'), 'order': 'id asc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
                                                
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft', 'verify','done','cancel'])]},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'verify': {'label': _('Waiting'), 'domain': [('state', '=', 'verify')]},
            'done': {'label': _('Done'), 'domain': [('state', '=', 'done')]}, 
            'cancel': {'label': _('Rejected'), 'domain': [('state', '=', 'cancel')]},
        }
           
        searchbar_inputs = {
            'id': {'input': 'id', 'label': _('Search in No#')},
            'employee_id.name': {'input': 'employee_id.name', 'label': _('Search in Employee')},
           
            'number': {'input': 'number', 'label': _('Search in Reference')},

        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

        project_groups = request.env['hr.payslip'].search([])

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
            if search_in in ('number', 'all'):
                search_domain = OR([search_domain, [('number', 'ilike', search)]])
            if search_in in ('employee_id.name', 'all'):
                search_domain = OR([search_domain, [('employee_id.name', 'ilike', search)]])
            domain += search_domain
 
        payslip_count = request.env['hr.payslip'].search_count(domain)

        pager = portal_pager(
            url="/my/payslips",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'seissuesarch_in': search_in, 'search': search},
            total=payslip_count,
            page=page,
            step=self._items_per_page
        )

        _payslips = request.env['hr.payslip'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_payslip_history'] = _payslips.ids[:100]

        grouped_payslips = [_payslips]
                
        paging(0,0,1)
        paging(grouped_payslips)
        
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_payslips': grouped_payslips,
            'page_name': 'payslip',
            'default_url': '/my/payslips',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        })
        return request.render("de_portal_payslips.portal_my_payslips", values)   

   
    @http.route(['/my/payslip/<int:payslip_id>'], type='http', auth="user", website=True)
    def portal_my_payslip(self, payslip_id, access_token=None, **kw):
        values = []

        id = payslip_id
        try:
            payslip_sudo = self._document_check_access('hr.payslip', payslip_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        next_id = 0
        pre_id = 0
        payslip_user_flag = 0

                
        payslip_id_list = paging(0,1,0)
        next_next_id = 0
        payslip_id_list.sort()
        length_list = len(payslip_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if payslip_id in payslip_id_list:
                payslip_id_loc = payslip_id_list.index(payslip_id)
                if payslip_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif payslip_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0

        values = self._payslips_get_page_view_values(payslip_sudo,next_id, pre_id, payslip_user_flag,access_token, **kw) 
        return request.render("de_portal_payslips.portal_my_payslip", values)

    @http.route(['/payslip/next/<int:payslip_id>'], type='http', auth="user", website=True)
    def portal_my_next_payslip(self, payslip_id, access_token=None, **kw):
        
        payslip_id_list = paging(0,1,0)
        next_next_id = 0
        payslip_id_list.sort()
        
        length_list = len(payslip_id_list)
        if length_list == 0:
            return request.redirect('/my')
        length_list = length_list - 1
        
        if payslip_id in payslip_id_list:
            payslip_id_loc = payslip_id_list.index(payslip_id)
            next_next_id = payslip_id_list[payslip_id_loc + 1] 
            next_next_id_loc = payslip_id_list.index(next_next_id)
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
            for ids in payslip_id_list:
                if ids < payslip_id:
                    buffer_smaller = ids
                if ids > payslip_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_larger:
                next_next_id = buffer_smaller
            elif buffer_smaller:
                next_next_id = buffer_larger
                
            next_next_id_loc = payslip_id_list.index(next_next_id)
            length_list = len(payslip_id_list)
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

        id = payslip_id
        try:
            payslip_sudo = self._document_check_access('hr.payslip', next_next_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        

        payslip_user_flag = 0


        values = self._payslips_get_page_view_values(payslip_sudo,next_id, pre_id, access_token, **kw) 
        return request.render("de_portal_payslips.portal_my_payslip", values)

  
    @http.route(['/payslip/pre/<int:payslip_id>'], type='http', auth="user", website=True)
    def portal_my_pre_payslip(self, payslip_id, access_token=None, **kw):
        
        payslip_id_list = paging(0,1,0)
        pre_pre_id = 0
        payslip_id_list.sort()
        length_list = len(payslip_id_list)
    
        if length_list == 0:
            return request.redirect('/my')
        
        length_list = length_list - 1
        if payslip_id in payslip_id_list:
            payslip_id_loc = payslip_id_list.index(payslip_id)
            pre_pre_id = payslip_id_list[payslip_id_loc - 1] 
            pre_pre_id_loc = payslip_id_list.index(payslip_id)

            if payslip_id_loc == 1:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in payslip_id_list:
                if ids < payslip_id:
                    buffer_smaller = ids
                if ids > payslip_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_smaller:
                pre_pre_id = buffer_smaller
            elif buffer_larger:
                pre_pre_id = buffer_larger
                
            pre_pre_id_loc = payslip_id_list.index(pre_pre_id)
            length_list = len(payslip_id_list)
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
            payslip_sudo = self._document_check_access('hr.payslip', pre_pre_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        

        payslip_user_flag = 0


        values = self._payslips_get_page_view_values(payslip_sudo, next_id,pre_id, access_token, **kw) 
        return request.render("de_portal_payslips.portal_my_payslip", values)

    