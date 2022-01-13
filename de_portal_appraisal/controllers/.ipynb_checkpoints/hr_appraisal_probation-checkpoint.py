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
import ast
appraisal_probation_list = []

def appraisal_probation_page_content(flag = 0):
    global appraisal_probation_list 
    managers = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    employees = request.env['hr.employee'].search([('user_id','=',http.request.env.context.get('uid'))])
    company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    return {
        'managers': managers,
        'employees' : employees,
        'appraisal_probation_list': appraisal_probation_list,
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
                
                
class CreateAppraisal(http.Controller):
    
    @http.route('/probation/line/save',type="http", website=True, auth='user')
    def appraisal_probation_template(self, **kw):
        probation = request.env['hr.appraisal.probation'].search([('id','=', kw.get('probationid'))])
        if probation.state in ('draft','confirmed'):
            probation.update({
                'knowledge': kw.get('knowledge'),
                'productivity': kw.get('productivity'),
                'quality_of_work': kw.get('quality_of_work'),
                'technical_skills': kw.get('technical_skills'),
                'analytical_skills': kw.get('analytical_skills'),
                'creativity': kw.get('creativity'),
                'team_player': kw.get('team_player'),
                'hardwork': kw.get('hardwork'),
                'communication_skills': kw.get('communication_skills'),
                'dependability': kw.get('dependability'),
                'initiative': kw.get('initiative'),
                'meet_deadline': kw.get('meet_deadline'),
                'discipline': kw.get('discipline'),
                'employee_can_excel': kw.get('employee_can_excel'),
                'improvement_is_required': kw.get('improvement_is_required'),
            })
            if kw.get('reviewed_employee') != 'blank':
                probation.update({
                    'reviewed_employee': kw.get('reviewed_employee')
                })    
            if kw.get('confirmation_status') == 'confirm':
                probation.update({
                    'gross_salary': kw.get('gross_salary'),
                    'grade': kw.get('grade'),
                    'with_from': kw.get('with_from'),
                })
            elif kw.get('confirmation_status') == 'extend':
                if  kw.get('probation_extension_period') != 'blank':
                    probation.update({
                        'probation_extension_period': kw.get('probation_extension_period'),
                    })
                
        if probation.state =='employee_waiting':
            probation.update({
                'employee_comment': kw.get('employee_comment'),
            })
        if probation.state =='employee_review':
            probation.update({
                'hr_comments': kw.get('hr_comments'),
            })
        if probation.state =='hr_review':
            probation.update({
                'comments': kw.get('comments'),
            })    
        return request.redirect('/appraisal/probation/%s'%(probation.id))
                   
        
        
class CustomerPortal(CustomerPortal):
    
    
    @http.route(['/action/confirm/probation/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_confirm_probation(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.probation'].sudo().browse(id)

        record.action_confirmed()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.probation', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        edit_probation = False
        edit_emp_probation = False
        edit_hod_probation = False
        edit_hr_probation = False
        values = self._probation_get_page_view_values(approval_sudo,edit_probation,edit_emp_probation, edit_hod_probation, edit_hr_probation,  **kw) 
        return request.redirect('/appraisal/probation/%s'%(record.id)) 
    
    @http.route(['/action/emp/review/probation/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_probation_emp_review(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.probation'].sudo().browse(id)

        record.action_waiting()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.probation', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        edit_probation = False
        edit_emp_probation = False
        edit_hod_probation = False
        edit_hr_probation = False
        values = self._probation_get_page_view_values(approval_sudo,edit_probation,edit_emp_probation, edit_hod_probation, edit_hr_probation,  **kw) 
        return request.redirect('/appraisal/probation/%s'%(record.id)) 
    
    @http.route(['/action/confirm/empreview/probation/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_confirm_empreview_probation(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.probation'].sudo().browse(id)

        record.action_review()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.probation', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        edit_probation = False
        edit_emp_probation = False
        edit_hod_probation = False
        edit_hr_probation = False
        values = self._probation_get_page_view_values(approval_sudo,edit_probation,edit_emp_probation, edit_hod_probation, edit_hr_probation,  **kw) 
        return request.redirect('/appraisal/probation/%s'%(record.id)) 
    
    @http.route(['/action/confirm/hrreview/probation/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_hr_confirm_probation(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.probation'].sudo().browse(id)

        record.action_hr_review()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.probation', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        edit_probation = False
        edit_emp_probation = False
        edit_hod_probation = False
        edit_hr_probation = False
        values = self._probation_get_page_view_values(approval_sudo,edit_probation,edit_emp_probation, edit_hod_probation, edit_hr_probation,  **kw) 
        return request.redirect('/appraisal/probation/%s'%(record.id))
    
    
    @http.route(['/action/confirm/hodreview/probation/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_confirm_hod_probation(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.probation'].sudo().browse(id)

        record.action_done()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.probation', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        edit_probation = False
        edit_emp_probation = False
        edit_hod_probation = False
        edit_hr_probation = False
        values = self._probation_get_page_view_values(approval_sudo,edit_probation,edit_emp_probation, edit_hod_probation, edit_hr_probation,  **kw) 
        return request.redirect('/appraisal/probation/%s'%(record.id))
    
    
    
    
    def _probation_get_page_view_values(self,probation, edit_probation,edit_emp_probation, edit_hod_probation, edit_hr_probation, next_id = 0,pre_id= 0, probation_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])         
        grade = request.env['grade.designation'].sudo().search([])
        values = {
            'page_name' : 'probation',
            'probation' : probation,
            'grade': grade,
            'probation_user_flag': probation_user_flag,
            'next_id' : next_id,
            'edit_probation': edit_probation,
            'edit_emp_probation': edit_emp_probation,
            'edit_hod_probation': edit_hod_probation,
            'edit_hr_probation': edit_hr_probation,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(probation, access_token, values, 'my_probation_history', False, **kwargs)

    
    @http.route(['/appraisal/probations', '/appraisal/probation/page/<int:page>'], type='http', auth="user", website=True)
    def portal_appraisal_probations(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'id': {'label': _('Default'), 'order': 'id asc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft', 'employee_waiting','confirmed','employee_review','hr_review','done'])]},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'waiting': {'label': _('Submitted'), 'domain': [('state', '=', 'employee_waiting')]},  
            'confirmed': {'label': _('Approved'), 'domain': [('state', '=', 'confirmed')]},
            'employee_review': {'label': _('Employee Review'), 'domain': [('state', '=', 'employee_review')]},
            'hr_review': {'label': _('HR Review'), 'domain': [('state', '=', 'hr_review')]},
            'done': {'label': _('Done'), 'domain': [('state', '=', 'done')]},
        }
           
        searchbar_inputs = {
            'id': {'input': 'id', 'label': _('Search in No#')},
            'name': {'input': 'name', 'label': _('Search in Name')},
            'employee_id.name': {'input': 'employee_id.name', 'label': _('Search in Employee')}, 
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

        appraisal_groups = request.env['hr.appraisal.probation'].search([])

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
            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain
        domain += ['|','|',
                   '|',('employee_id.user_id', '=', http.request.env.context.get('uid'))
                   ,('employee_id.company_id.hr_id.user_id', '=', http.request.env.context.get('uid')),
                   ('employee_id.parent_id.user_id', '=', http.request.env.context.get('uid')),('employee_id.department_id.manager_id.user_id', '=', http.request.env.context.get('uid'))]
        probation_count = request.env['hr.appraisal.probation'].sudo().search_count(domain)

        pager = portal_pager(
            url="/appraisal/probations",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=probation_count,
            page=page,
            step=self._items_per_page
        )
        _probations = request.env['hr.appraisal.probation'].sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_probation_history'] = _probations.ids[:100]
        grouped_probations = [_probations]                
        paging(0,0,1)
        paging(grouped_probations)
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_probations': grouped_probations,
            'page_name': 'probation',
            'default_url': '/appraisal/probations',
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
        return request.render("de_portal_appraisal.portal_appraisal_probations", values)

   
    @http.route(['/appraisal/probation/<int:probation_id>'], type='http', auth="user", website=True)
    def portal_appraisal_probation(self, probation_id, access_token=None, **kw):
        values = []
        active_user = http.request.env.context.get('uid')
        probation_user = []
        id = probation_id
        try:
            probation_sudo = self._document_check_access('hr.appraisal.probation', probation_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')        

        probation_user_flag = 0
                
        probation_id_list = paging(0,1,0)
        next_id = 0
        pre_id = 0
        next_next_id = 0
        probation_id_list.sort()
        length_list = len(probation_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if probation_id in probation_id_list:
                probation_id_loc = probation_id_list.index(probation_id)
                if probation_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif probation_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0            
        edit_probation = False
        edit_emp_probation = False
        edit_hod_probation = False
        edit_hr_probation = False
        values = self._probation_get_page_view_values(probation_sudo,edit_probation,edit_emp_probation, edit_hod_probation, edit_hr_probation,next_id, pre_id, probation_user_flag,access_token, **kw) 
        return request.render("de_portal_appraisal.portal_appraisal_probation", values)
    
    
    # Appraisal Edit probation
    
    @http.route(['/appraisal/edit/probation/<int:probation_id>'], type='http', auth="user", website=True)
    def edit_portal_appraisal_probation(self, probation_id, access_token=None, **kw):
        values = []
        active_user = http.request.env.context.get('uid')
        probation_user = []
        id = probation_id
        try:
            probation_sudo = self._document_check_access('hr.appraisal.probation', probation_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')        

        probation_user_flag = 0
                
        probation_id_list = paging(0,1,0)
        next_id = 0
        pre_id = 0
        next_next_id = 0
        probation_id_list.sort()
        length_list = len(probation_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if probation_id in probation_id_list:
                probation_id_loc = probation_id_list.index(probation_id)
                if probation_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif probation_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0
            
        edit_probation = False
        edit_emp_probation = False
        edit_hod_probation = False
        edit_hr_probation = False
        if probation_sudo.state in ('draft','confirmed') and probation_sudo.employee_id.parent_id.user_id.id == http.request.env.context.get('uid'):
            edit_probation = True
        if probation_sudo.state =='employee_waiting' and probation_sudo.employee_id.user_id.id == http.request.env.context.get('uid'):
            edit_emp_probation = True   
        if probation_sudo.state =='employee_review' and probation_sudo.employee_id.company_id.hr_id.user_id.id == http.request.env.context.get('uid'):
            edit_hr_probation = True
        if probation_sudo.state =='hr_review' and probation_sudo.employee_id.department_id.manager_id.user_id.id == http.request.env.context.get('uid'):
            edit_hod_probation = True    
        
        values = self._probation_get_page_view_values(probation_sudo, edit_probation,edit_emp_probation, edit_hod_probation, edit_hr_probation,next_id, pre_id, probation_user_flag,access_token, **kw) 
        return request.render("de_portal_appraisal.portal_appraisal_probation", values)

    

    @http.route(['/probation/next/<int:probation_id>'], type='http', auth="user", website=True)
    def portal_probation_next(self, probation_id, access_token=None, **kw):
        
        probation_id_list = paging(0,1,0)
        next_next_id = 0
        probation_id_list.sort()
        
        length_list = len(probation_id_list)
        if length_list == 0:
            return request.redirect('/my')
        length_list = length_list - 1
        
        if probation_id in probation_id_list:
            probation_id_loc = probation_id_list.index(probation_id)
            next_next_id = probation_id_list[probation_id_loc + 1] 
            next_next_id_loc = probation_id_list.index(next_next_id)
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
            for ids in probation_id_list:
                if ids < probation_id:
                    buffer_smaller = ids
                if ids > probation_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_larger:
                next_next_id = buffer_smaller
            elif buffer_smaller:
                next_next_id = buffer_larger
                
            next_next_id_loc = probation_id_list.index(next_next_id)
            length_list = len(probation_id_list)
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
        probation_user = []
        id = probation_id
        try:
            probation_sudo = self._document_check_access('hr.appraisal.probation', next_next_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        probation_user_flag = 0

        edit_probation = False
        edit_emp_probation = False
        edit_hod_probation = False
        edit_hr_probation = False
        values = self._probation_get_page_view_values(probation_sudo, edit_probation,edit_emp_probation, edit_hod_probation, edit_hr_probation,next_id, pre_id, access_token, **kw) 
        return request.render("de_portal_appraisal.portal_appraisal_probation", values)

  
    @http.route(['/probation/pre/<int:probation_id>'], type='http', auth="user", website=True)
    def portal_probation_previous(self, probation_id, access_token=None, **kw):
        
        probation_id_list = paging(0,1,0)
        pre_pre_id = 0
        probation_id_list.sort()
        length_list = len(probation_id_list)
    
        if length_list == 0:
            return request.redirect('/my')
        
        length_list = length_list - 1
        if probation_id in probation_id_list:
            probation_id_loc = probation_id_list.index(probation_id)
            pre_pre_id = probation_id_list[probation_id_loc - 1] 
            pre_pre_id_loc = probation_id_list.index(probation_id)

            if probation_id_loc == 1:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in probation_id_list:
                if ids < probation_id:
                    buffer_smaller = ids
                if ids > probation_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_smaller:
                pre_pre_id = buffer_smaller
            elif buffer_larger:
                pre_pre_id = buffer_larger
                
            pre_pre_id_loc = probation_id_list.index(pre_pre_id)
            length_list = len(probation_id_list)
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
        probation_user = []
        id = pre_pre_id
        try:
            probation_sudo = self._document_check_access('hr.appraisal.probation', pre_pre_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        probation_user_flag = 0
        edit_probation = False
        edit_emp_probation = False
        edit_hod_probation = False
        edit_hr_probation = False
        values = self._probation_get_page_view_values(probation_sudo,edit_probation,edit_emp_probation, edit_hod_probation, edit_hr_probation, next_id,pre_id, access_token, **kw) 
        return request.render("de_portal_appraisal.portal_appraisal_probation", values)
    
##############################