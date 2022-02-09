# # -*- coding: utf-8 -*-

from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.osv import expression
from odoo.exceptions import UserError
from collections import OrderedDict
from operator import itemgetter
from datetime import datetime, date
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


def action_check_warning(warning):
    company_info = request.env['res.users'].sudo().search([('id', '=', http.request.env.context.get('uid'))])
    return {
        'warning_message': warning,
        'company_info': company_info
    }

def timesheet_page_content(flag=0):
    
    employees = request.env['hr.employee'].sudo().search([])
    partners = request.env['res.ora.client'].sudo().search([])
    company_info = request.env['res.users'].sudo().search([('id', '=', http.request.env.context.get('uid'))])
    projects = request.env['project.project'].sudo().search([('ora_enabled','=', True),('ora_close_date','>=',fields.date.today()),('ora_status','=','approved'),('company_id','=',company_info.company_id.id)])
    employee_name = employees
    return {
        'projects': projects,
        'partners': partners,
        'employees': employees,
        'success_flag': flag,
        'company_info': company_info
    }

def timesheet_line_page_content(project):
    company_info = request.env['res.users'].sudo().search([('id', '=', http.request.env.context.get('uid'))])
    incharge_dept = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))], limit=1)
    uprojects = request.env['project.project'].sudo().search([('id','=',project)])
    employees = request.env['hr.employee'].sudo().search([('department_id','=', incharge_dept.department_id.id),('id','!=',incharge_dept.id),('company_id','=',incharge_dept.company_id.id)])
    upartner = request.env['res.ora.client'].search([('id','=',uprojects.ora_client_id.id)])
    
    return {
        'partner': upartner,
        'project': uprojects,
        'emps': employees,
        'company_info': company_info
    }


class CreateTimesheet(http.Controller):

    @http.route('/timesheet/create/', type="http", website=True, auth='user')
    def timesheet_create_template(self, **kw):
        return request.render("de_portal_timesheet.project_timesheet_template", timesheet_page_content())
    
    @http.route('/timesheet/report/', type="http", website=True, auth='user')
    def timesheet_report_template(self, **kw):
        return request.render("de_portal_timesheet.print_timesheet_report", timesheet_page_content())


    @http.route('/project/timesheet/next', type="http", auth="public", website=True)
    def project_timesheet_next_forms(self, **kw):
        project = int(kw.get('project_id'))
        return request.render("de_portal_timesheet.portal_create_timesheet_report_lines", timesheet_line_page_content(project))

    
    @http.route('/project/timesheet/create', type="http", auth="public", website=True)
    def project_timesheet_save(self, **kw):
        project = int(kw.get('project_id'))
        editable_employee=request.env['hr.employee'].search([('id','=',http.request.env.context.get('uid'))], limit=1)
        exist_timesheet_portal=request.env['hr.timesheet.report.line'].sudo().search([('employee_id','=',editable_employee.id),('date_from','>=',kw.get('date_from')),('date_to','<=', kw.get('date_to')),('timesheet_repo_id.state','in',('draft','submitted','approved'))], limit=1)
        exist_in_timesheet_portal=request.env['hr.timesheet.report.line'].sudo().search([('employee_id','=',editable_employee.id),('date_from','<=',kw.get('date_from')),('date_to','>=', kw.get('date_from')),('timesheet_repo_id.state','in',('draft','submitted','approved'))], limit=1)
        exist_out_timesheet_portal=request.env['hr.timesheet.report.line'].sudo().search([('employee_id','=',editable_employee.id),('date_from','<=',kw.get('date_to')),('date_to','>=', kw.get('date_to')),('timesheet_repo_id.state','in',('draft','submitted','approved'))], limit=1)
        
        if exist_timesheet_portal:
            warning_message='Project Timesheet already created for this range! Date From: '+str(exist_timesheet_portal.date_from.strftime('%d/%b/%y'))+' Date To: '+str(exist_timesheet_portal.date_to.strftime('%d/%b/%y'))+' For Employee '+str(editable_employee.name)
            return request.render("de_portal_timesheet.submited_validation", action_check_warning(warning_message))

        if exist_in_timesheet_portal:
            warning_message='Project Timesheet already created for this range! Date From: '+str(exist_in_timesheet_portal.date_from.strftime('%d/%b/%y'))+' Date To: '+str(exist_in_timesheet_portal.date_to.strftime('%d/%b/%y'))+' For Employee '+str(editable_employee.name)
            return request.render("de_portal_timesheet.submited_validation", action_check_warning(warning_message))
        if exist_out_timesheet_portal:
            warning_message='Project Timesheet already created for this range! Date From: '+str(exist_out_timesheet_portal.date_from.strftime('%d/%b/%y'))+' Date To: '+str(exist_out_timesheet_portal.date_to.strftime('%d/%b/%y'))+' For Employee '+str(editable_employee.name) 
            return request.render("de_portal_timesheet.submited_validation", action_check_warning(warning_message))
        
                    
        timesheet_portal=request.env['hr.timesheet.report'].sudo().search([('project_id','=',project),('state','in',('submitted','approved')),('date_from','>=',kw.get('date_from')),('date_to','<=', kw.get('date_to'))], limit=1)
        in_timesheet_portal=request.env['hr.timesheet.report'].sudo().search([('project_id','=',project),('state','in',('submitted','approved')),('date_from','<=',kw.get('date_from')),('date_to','>=', kw.get('date_from'))], limit=1)
        out_timesheet_portal=request.env['hr.timesheet.report'].sudo().search([('project_id','=',project),('state','in',('submitted','approved')),('date_from','<=',kw.get('date_to')),('date_to','>=', kw.get('date_to'))], limit=1)
        
        if timesheet_portal:
            warning_message='Project Timesheet already created for this range! Date From: '+str(timesheet_portal.date_from.strftime('%d/%b/%y'))+' Date To: '+str(timesheet_portal.date_to.strftime('%d/%b/%y'))
            return request.render("de_portal_timesheet.submited_validation", action_check_warning(warning_message))

            
        if in_timesheet_portal:
            warning_message='Project Timesheet already created for this range! Date From: '+str(in_timesheet_portal.date_from.strftime('%d/%b/%y'))+' Date To: '+str(in_timesheet_portal.date_to.strftime('%d/%b/%y'))
            return request.render("de_portal_timesheet.submited_validation", action_check_warning(warning_message))
            
        if out_timesheet_portal:
            warning_message='Project Timesheet already created for this range! Date From: '+str(out_timesheet_portal.date_from.strftime('%d/%b/%y'))+' Date To: '+str(out_timesheet_portal.date_to.strftime('%d/%b/%y')) 
            return request.render("de_portal_timesheet.submited_validation", action_check_warning(warning_message))

        vals = {
            'incharge_id': request.env['hr.employee'].sudo().search([('user_id','=', http.request.env.context.get('uid'))]).id,
            'partner_id': int(kw.get('partner_id')),
            'project_id': int(kw.get('project_id')),
            'date_from': kw.get('docsdate_from'),
            'date_to': kw.get('docsdate_to'),
        }
        sheet_report = request.env['hr.timesheet.report'].sudo().create(vals)        
        
        vals = {
            'timesheet_repo_id': sheet_report.id,
            'project_id': project,
            'employee_id': int(kw.get('employee_id')),
            'date_from':  kw.get('date_from'),
            'date_to': kw.get('date_to'),
        }
        timesheet_line=request.env['hr.timesheet.report.line'].sudo().create(vals)
        return request.redirect('/project/timesheet/edit/%s'%(sheet_report.id))
    
    
    
    @http.route('/project/timesheet/edit/save', type="http", auth="public", website=True)
    def project_timesheet_edit_save(self, **kw):
        project = int(kw.get('project_id'))
        timesheet = int(kw.get('timesheet_id'))
        editable_employee=request.env['hr.employee'].search([('id','=',int(kw.get('employee_id')))], limit=1)
        exist_timesheet_portal=request.env['hr.timesheet.report.line'].sudo().search([('employee_id','=',editable_employee.id),('date_from','>=',kw.get('date_from')),('date_to','<=', kw.get('date_to')),('timesheet_repo_id.state','in',('draft','submitted','approved'))], limit=1)
        exist_in_timesheet_portal=request.env['hr.timesheet.report.line'].sudo().search([('employee_id','=',editable_employee.id),('date_from','<=',kw.get('date_from')),('date_to','>=', kw.get('date_from')),('timesheet_repo_id.state','in',('draft','submitted','approved'))], limit=1)
        exist_out_timesheet_portal=request.env['hr.timesheet.report.line'].sudo().search([('employee_id','=',editable_employee.id),('date_from','<=',kw.get('date_to')),('date_to','>=', kw.get('date_to')),('timesheet_repo_id.state','in',('draft','submitted','approved'))], limit=1)
        
        if exist_timesheet_portal:
            warning_message='Project Timesheet already created for this range! Date From: '+str(exist_timesheet_portal.date_from.strftime('%d/%b/%y'))+' Date To: '+str(exist_timesheet_portal.date_to.strftime('%d/%b/%y'))+' For Employee '+str(editable_employee.name)+' For Project '+str(exist_timesheet_portal.project_id.name)
            return request.render("de_portal_timesheet.submited_validation", action_check_warning(warning_message))

        if exist_in_timesheet_portal:
            warning_message='Project Timesheet already created for this range! Date From: '+str(exist_in_timesheet_portal.date_from.strftime('%d/%b/%y'))+' Date To: '+str(exist_in_timesheet_portal.date_to.strftime('%d/%b/%y'))+' Employee '+str(editable_employee.name)+ ' For Project '+str(exist_in_timesheet_portal.project_id.name)
            return request.render("de_portal_timesheet.submited_validation", action_check_warning(warning_message))
        if exist_out_timesheet_portal:
            warning_message='Project Timesheet already created for this range! Date From: '+str(exist_out_timesheet_portal.date_from.strftime('%d/%b/%y'))+' Date To: '+str(exist_out_timesheet_portal.date_to.strftime('%d/%b/%y'))+' Employee '+str(editable_employee.name)+' For Project '+str(exist_out_timesheet_portal.project_id.name) 
            return request.render("de_portal_timesheet.submited_validation", action_check_warning(warning_message))
        
                    
        timesheet_portal=request.env['hr.timesheet.report'].sudo().search([('project_id','=',project),('state','in',('submitted','approved')),('date_from','>=',kw.get('date_from')),('date_to','<=', kw.get('date_to'))], limit=1)
        in_timesheet_portal=request.env['hr.timesheet.report'].sudo().search([('project_id','=',project),('state','in',('submitted','approved')),('date_from','<=',kw.get('date_from')),('date_to','>=', kw.get('date_from'))], limit=1)
        out_timesheet_portal=request.env['hr.timesheet.report'].sudo().search([('project_id','=',project),('state','in',('submitted','approved')),('date_from','<=',kw.get('date_to')),('date_to','>=', kw.get('date_to'))], limit=1)
        
        if timesheet_portal:
            warning_message='Project Timesheet already created for this range! Date From: '+str(timesheet_portal.date_from.strftime('%d/%b/%y'))+' Date To: '+str(timesheet_portal.date_to.strftime('%d/%b/%y'))
            return request.render("de_portal_timesheet.submited_validation", action_check_warning(warning_message))

            
        if in_timesheet_portal:
            warning_message='Project Timesheet already created for this range! Date From: '+str(in_timesheet_portal.date_from.strftime('%d/%b/%y'))+' Date To: '+str(in_timesheet_portal.date_to.strftime('%d/%b/%y'))
            return request.render("de_portal_timesheet.submited_validation", action_check_warning(warning_message))
            
        if out_timesheet_portal:
            warning_message='Project Timesheet already created for this range! Date From: '+str(out_timesheet_portal.date_from.strftime('%d/%b/%y'))+' Date To: '+str(out_timesheet_portal.date_to.strftime('%d/%b/%y')) 
            return request.render("de_portal_timesheet.submited_validation", action_check_warning(warning_message))

                
        vals = {
            'timesheet_repo_id': timesheet,
            'project_id': project,
            'employee_id': int(kw.get('employee_id')),
            'date_from':  kw.get('date_from'),
            'date_to': kw.get('date_to'),
        }
        timesheet_line=request.env['hr.timesheet.report.line'].sudo().create(vals)
        return request.redirect('/project/timesheet/edit/%s'%(timesheet))


class CustomerPortal(CustomerPortal):
    
    
    def _show_timesheet_report_portal(self, model, report_type, employee,project, start_date, end_date, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s", report_type))

        report_sudo = request.env.ref(report_ref).with_user(SUPERUSER_ID)

        if not isinstance(report_sudo, type(request.env['ir.actions.report'])):
            raise UserError(_("%s is not the reference of a report", report_ref))

        if hasattr(model, 'company_id'):
            report_sudo = report_sudo.with_company(model.company_id)

        method_name = '_render_qweb_%s' % (report_type)
        report = getattr(report_sudo, method_name)([model], data={'report_type': report_type,'employee':employee,'project':project,'start_date':start_date,'end_date':end_date})[0]
        reporthttpheaders = [
            ('Content-Type', 'application/pdf' if report_type == 'pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        if report_type == 'pdf' and download:
            filename = "%s.pdf" % (re.sub('\W+', '-', model._get_report_base_filename()))
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))
        return request.make_response(report, headers=reporthttpheaders)


    
    @http.route('/project/timesheet/print',type="http", website=True,download=False, auth='user')
    def action_print_timesheet_report(self, **kw):
        report_type='pdf'
        order_sudo = 'hr.timesheet.report'
        download = False
        employee = request.env['hr.employee'].search([('user_id','=',http.request.env.context.get('uid'))]).id
        project = int(kw.get('project_id'))
        start_date = kw.get('date_from')
        end_date = kw.get('date_to')
        return self._show_timesheet_report_portal(model=order_sudo, report_type=report_type,employee=employee, project=project, start_date=start_date, end_date=end_date, report_ref='de_portal_timesheet.timesheet_attendance_report_action', download=download)
    


    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'ptimesheet_count' in counters:
            values['ptimesheet_count'] = request.env['hr.timesheet.report'].search_count(
                [('incharge_id.user_id', '=', http.request.env.context.get('uid'))])
        return values

    def _ptimesheet_get_page_view_values(self, ptimesheet,edit_timesheet=0, next_id=0, pre_id=0, ptimesheet_user_flag=0, access_token=None,
                                      **kwargs):
        company_info = request.env['res.users'].search([('id', '=', http.request.env.context.get('uid'))])
        incharge_dept = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))], limit=1)
        employees = request.env['hr.employee'].sudo().search([('department_id','=', incharge_dept.department_id.id),('id','!=',incharge_dept.id),('company_id','=',incharge_dept.company_id.id)])
                                                              
        values = {
            'page_name': 'ptimesheet',
            'ptimesheet': ptimesheet,
            'emps': employees,
            'edit_timesheet': edit_timesheet,
            'current_date': fields.date.today(),
            'ptimesheet_user_flag': ptimesheet_user_flag,
            'next_id': next_id,
            'company_info': company_info,
            'pre_id': pre_id,
        }
        return self._get_page_view_values(ptimesheet, access_token, values, 'my_ptimesheet_history', False, **kwargs)
    
    
    @http.route(['/project/timesheets', '/project/timesheet/page/<int:page>'], type='http', auth="user", website=True)
    def portal_project_timesheets_report(self, page=1, sortby='name', search='', **kw):
        # only website_designer should access the page Management
        grouped_ptimesheets = request.env['hr.timesheet.report']
        searchbar_sortings = {
            'name': {'label': _('Sort by Name'), 'order': 'name'},
            'id': {'label': _('Sort by ID'), 'order': 'id'},
        }
        # default sortby order
        sort_order = searchbar_sortings.get(sortby, 'id')
        domain = []
        if search:
            domain += []
        grouped_ptimesheets = request.env['hr.timesheet.report'].sudo().search([('incharge_id.user_id','=',http.request.env.context.get('uid'))])        
        timesheets_count = len(grouped_ptimesheets)
        step = 50
        pager = portal_pager(
            url="/project/timesheets",
            url_args={'sortby': sortby},
            total=timesheets_count,
            page=grouped_ptimesheets,
            step=step
        )
        pages = grouped_ptimesheets
        values = {
            'pager': pager,
            'grouped_ptimesheets': grouped_ptimesheets,
            'search': search,
            'sortby': sortby,
            'searchbar_sortings': searchbar_sortings,
        }
        return request.render("de_portal_timesheet.portal_project_timesheets", values)


    @http.route(['/project/timesheet/reset/<int:timesheet_id>'], type='http', auth="user", website=True)
    def portal_project_timesheet_reset(self, timesheet_id, access_token=None, **kw):
        timesheet_sudo=request.env['hr.timesheet.report'].sudo().search([('id','=', timesheet_id)], limit=1)
        timesheet_sudo.action_draft()
        next_id = 0
        pre_id = 0
        edit_timesheet = 0
        timesheet_user_flag = 0
        values = self._ptimesheet_get_page_view_values(timesheet_sudo, edit_timesheet, next_id, pre_id, access_token, **kw)
        return request.render("de_portal_timesheet.portal_project_timesheet", values)
    
    @http.route(['/project/timesheet/<int:timesheet_id>'], type='http', auth="user", website=True)
    def portal_project_timesheet(self, timesheet_id, access_token=None, **kw):
        try:
            timesheet_sudo = self._document_check_access('hr.timesheet.report', timesheet_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        next_id = 0
        pre_id = 0
        edit_timesheet = 0
        timesheet_user_flag = 0
        values = self._ptimesheet_get_page_view_values(timesheet_sudo, edit_timesheet, next_id, pre_id, access_token, **kw)
        return request.render("de_portal_timesheet.portal_project_timesheet", values)
    
    
    @http.route(['/project/timesheet/edit/<int:timesheet_id>'], type='http', auth="user", website=True)
    def portal_project_timesheet_edit(self, timesheet_id, access_token=None, **kw):
        try:
            timesheet_sudo = self._document_check_access('hr.timesheet.report', timesheet_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        next_id = 0
        pre_id = 0
        edit_timesheet = 1
        timesheet_user_flag = 0
        values = self._ptimesheet_get_page_view_values(timesheet_sudo, edit_timesheet, next_id, pre_id, access_token, **kw)
        return request.render("de_portal_timesheet.portal_project_timesheet", values)
    
    @http.route(['/timesheet/line/delete/<int:line_id>'], type='http', auth="user", website=True)
    def portal_project_timesheet_delete(self, line_id, access_token=None, **kw):
        timesheet_line=request.env['hr.timesheet.report.line'].sudo().search([('id','=',line_id)], limit=1)
        timesheet_id = timesheet_line.timesheet_repo_id.id
        timesheet_line.unlink()
        try:
            timesheet_sudo = self._document_check_access('hr.timesheet.report', timesheet_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        next_id = 0
        pre_id = 0
        edit_timesheet = 1
        timesheet_user_flag = 0
        values = self._ptimesheet_get_page_view_values(timesheet_sudo, edit_timesheet, next_id, pre_id, access_token, **kw)
        return request.render("de_portal_timesheet.portal_project_timesheet", values)
    

    @http.route(['/project/timesheet/submit/<int:timesheet_id>'], type='http', auth="user", website=True)
    def portal_project_timesheet_submit(self, timesheet_id, access_token=None, **kw):
        timesheet=request.env['hr.timesheet.report'].sudo().search([('id','=',timesheet_id)], limit=1)
        timesheet.action_submit()
        return request.render("de_portal_timesheet.ptimesheet_submited", {})



     