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

def approval_page_content(flag = 0):
    partner = request.env['res.partner'].search([])
    category = request.env['approval.category'].search([])

    return {
        'approval_data': category,
        'oweners_res_partner' : partner,
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
    @http.route('/approval/create/',type="http", website=True, auth='user')
    def approvals_create_template(self, **kw):
        return request.render("de_portal_approvals.create_approval",approval_page_content()) 
    



class CustomerPortal(CustomerPortal):
    
    @http.route(['/app/approval/accept/<int:approval_id>'], type='http', auth="public", website=True)
    def approval_accept(self,approval_id ,**kw):
        id=approval_id
        recrd = request.env['approval.request'].sudo().browse(id)
        recrd.action_approve()
        approvals_page = CustomerPortal()
        return request.render("de_portal_approvals.approval_submited", {})
        
    @http.route(['/app/approval/reject/<int:approval_id>'], type='http', auth="public", website=True)
    def approval_reject(self,approval_id ,**kw):
        id=approval_id
        recrd = request.env['approval.request'].sudo().browse(id)
        recrd.action_refuse()
        approvals_page = CustomerPortal()
        return request.render("de_portal_approvals.approval_refused", {})
        
    @http.route(['/app/approval/approve/<int:approval_id>'], type='http', auth="public", website=True)
    def approval(self,approval_id , access_token=None, **kw):
        id=approval_id
        record = request.env['approval.request'].sudo().browse(id)

        record.action_approve()
        try:
            approval_sudo = self._document_check_access('approval.request', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._approval_get_page_view_values(approval_sudo, **kw) 
        return request.render("de_portal_approvals.approval_submited", {})
        
        
    @http.route(['/app/approval/refuse/<int:approval_id>'], type='http', auth="public", website=True)
    def refuse(self,approval_id , access_token=None, **kw):
        id=approval_id
        recrd = request.env['approval.request'].sudo().browse(id)

        recrd.action_refuse()
        try:
            approval_sudo = self._document_check_access('approval.request', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        values = self._approval_get_page_view_values(approval_sudo, **kw) 
        return request.render("de_portal_approvals.approval_refused", {})
    
    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'approval_count' in counters:
            values['approval_count'] = request.env['approval.request'].search_count([('approver_ids.user_id.id','=',http.request.env.context.get('uid') )])
        return values
  
    def _approval_get_page_view_values(self,approval, next_id = 0,pre_id= 0, approver_user_flag = 0, access_token = None, **kwargs):
        values = {
            'page_name' : 'approval',
            'approval' : approval,
            'approver_user_flag': approver_user_flag,
            'next_id' : next_id,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(approval, access_token, values, 'my_approvals_history', False, **kwargs)

    @http.route(['/my/approvals', '/my/approvals/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_approvals(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'id': {'label': _('Default'), 'order': 'id asc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('request_status', 'in', ['new', 'pending','approved','refused','cancel'])]},
            'new': {'label': _('To Submit'), 'domain': [('request_status', '=', 'new')]},
            'pending': {'label': _('Submitted'), 'domain': [('request_status', '=', 'pending')]},  
            'approved': {'label': _('Approved'), 'domain': [('request_status', '=', 'approved')]},
            'refused': {'label': _('Refused'), 'domain': [('request_status', '=', 'refused')]}, 
            'cancel': {'label': _('Cancel'), 'domain': [('request_status', '=', 'cancel')]},
        }
           
        searchbar_inputs = {
            
            'name': {'input': 'name', 'label': _('Search in Name')},
            'reason': {'input': 'reason', 'label': _('Search in Description')},
            'id': {'input': 'id', 'label': _('Search in Ref#')},
            'category_id.name': {'input': 'category_id.name', 'label': _('Search in Category')},
            'request_owner_id.name': {'input': 'request_owner_id.name', 'label': _('Search in Request Owner')},
            'partner_id.name': {'input': 'partner_id.name', 'label': _('Search in Contact')},
            'request_status': {'input': 'request_status', 'label': _('Search in Stages')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

        project_groups = request.env['approval.request'].search([])

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
            if search_in in ('reason', 'all'):
                search_domain = OR([search_domain, [('reason', 'ilike', search)]])
            if search_in in ('category_id.name', 'all'):
                search_domain = OR([search_domain, [('category_id.name', 'ilike', search)]])
            if search_in in ('request_owner_id.name', 'all'):
                search_domain = OR([search_domain, [('request_owner_id.name', 'ilike', search)]])
            if search_in in ('partner_id.name', 'all'):
                search_domain = OR([search_domain, [('partner_id.name', 'ilike', search)]])
            if search_in in ('request_status', 'all'):
                search_domain = OR([search_domain, [('request_status', 'ilike', search)]])
            domain += search_domain
 
        approval_count = request.env['approval.request'].search_count(domain)

        pager = portal_pager(
            url="/my/Approvals",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'seissuesarch_in': search_in, 'search': search},
            total=approval_count,
            page=page,
            step=self._items_per_page
        )

        _approvals = request.env['approval.request'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_approvals_history'] = _approvals.ids[:100]

        grouped_approvals = [_approvals]
                
        paging(0,0,1)

        paging(grouped_approvals)
        
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_approvals': grouped_approvals,
            'page_name': 'approval',
            'default_url': '/my/approvals',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        })
        return request.render("de_portal_approvals.portal_my_approvals", values)   

   
    @http.route(['/my/approval/<int:approval_id>'], type='http', auth="user", website=True)
    def portal_my_approval(self, approval_id, access_token=None, **kw):
        values = []
        active_user = http.request.env.context.get('uid')
        approver_user = []
        id = approval_id
        try:
            approval_sudo = self._document_check_access('approval.request', approval_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        record = request.env['approval.request'].sudo().browse(id)
        for aprover in record.approver_ids:
            approver_user.append(aprover.user_id.id)
        next_id = 0
        pre_id = 0
        approver_user_flag = 0
        for user in  approver_user:
            if user == active_user:
                approver_user_flag = 1
                
        approval_id_list = paging(0,1,0)
        next_next_id = 0
        approval_id_list.sort()
        length_list = len(approval_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if approval_id in approval_id_list:
                approval_id_loc = approval_id_list.index(approval_id)
                if approval_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif approval_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0

        values = self._approval_get_page_view_values(approval_sudo,next_id, pre_id, approver_user_flag,access_token, **kw) 
        return request.render("de_portal_approvals.portal_my_approval", values)

    @http.route(['/approval/next/<int:approval_id>'], type='http', auth="user", website=True)
    def portal_my_next_approval(self, approval_id, access_token=None, **kw):
        
        approval_id_list = paging(0,1,0)
        next_next_id = 0
        approval_id_list.sort()
        
        length_list = len(approval_id_list)
        if length_list == 0:
            return request.redirect('/my')
        length_list = length_list - 1
        
        if approval_id in approval_id_list:
            approval_id_loc = approval_id_list.index(approval_id)
            next_next_id = approval_id_list[approval_id_loc + 1] 
            next_next_id_loc = approval_id_list.index(next_next_id)
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
            for ids in approval_id_list:
                if ids < approval_id:
                    buffer_smaller = ids
                if ids > approval_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_larger:
                next_next_id = buffer_smaller
            elif buffer_smaller:
                next_next_id = buffer_larger
                
            next_next_id_loc = approval_id_list.index(next_next_id)
            length_list = len(approval_id_list)
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
        approver_user = []
        id = approval_id
        try:
            approval_sudo = self._document_check_access('approval.request', next_next_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        record = request.env['approval.request'].sudo().browse(id)
        for aprover in record.approver_ids:
            approver_user.append(aprover.user_id.id)
        approver_user_flag = 0
        for user in  approver_user:
            if user == active_user:
                approver_user_flag = 1

        values = self._approval_get_page_view_values(approval_sudo,next_id, pre_id, access_token, **kw) 
        return request.render("de_portal_approvals.portal_my_approval", values)

  
    @http.route(['/approval/pre/<int:approval_id>'], type='http', auth="user", website=True)
    def portal_my_pre_approval(self, approval_id, access_token=None, **kw):
        
        approval_id_list = paging(0,1,0)
        pre_pre_id = 0
        approval_id_list.sort()
        length_list = len(approval_id_list)
    
        if length_list == 0:
            return request.redirect('/my')
        
        length_list = length_list - 1
        if approval_id in approval_id_list:
            approval_id_loc = approval_id_list.index(approval_id)
            pre_pre_id = approval_id_list[approval_id_loc - 1] 
            pre_pre_id_loc = approval_id_list.index(approval_id)

            if approval_id_loc == 1:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in approval_id_list:
                if ids < approval_id:
                    buffer_smaller = ids
                if ids > approval_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_smaller:
                pre_pre_id = buffer_smaller
            elif buffer_larger:
                pre_pre_id = buffer_larger
                
            pre_pre_id_loc = approval_id_list.index(pre_pre_id)
            length_list = len(approval_id_list)
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
        approver_user = []
        id = pre_pre_id
        try:
            approval_sudo = self._document_check_access('approval.request', pre_pre_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        record = request.env['approval.request'].sudo().browse(id)
        for aprover in record.approver_ids:
            approver_user.append(aprover.user_id.id)
        approver_user_flag = 0
        for user in  approver_user:
            if user == active_user:
                approver_user_flag = 1

        values = self._approval_get_page_view_values(approval_sudo, next_id,pre_id, access_token, **kw) 
        return request.render("de_portal_approvals.portal_my_approval", values)
