# # -*- coding: utf-8 -*-

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

def get_account_statement(flag = 0):
    accounts = request.env['account.account'].search([('is_publish','=', True)])
    user = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    partners = request.env['res.partner'].search([('id','=', user.partner_id.id)])
    journal_items = request.env['account.move.line'].search([])
    company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    
    return {
        'accounts' : accounts,
        'partners' : partners,
        'journal_items': journal_items,
        'company_info' : company_info,
    }
   
 
def get_account_statement_lines(account, partner, start_date, end_date):
    journal_items = request.env['account.move.line'].search(['&','&',('account_id','=',account),('date','>=',start_date),('date','<=',end_date)])
    return {
        'journal_items': journal_items,
    }



    
        
class AccountStatements(http.Controller):

    @http.route('/account/statement',type="http", website=True, auth='user')
    def portal_my_account_statement(self, **kw):
        return request.render("de_portal_accounting.portal_my_account_statement",get_account_statement()) 
    
    @http.route('/account/statement/views', type="http", auth="public", website=True)
    def account_statement_views(self, **kw):
        account = int(kw.get('account_id'))
        partner = int(kw.get('partner_id'))
        start_date = kw.get('date_start')
        end_date = kw.get('date_end')
        return request.render("de_portal_accounting.journal_item_page_template", get_account_statement_lines(account, partner, start_date, end_date))
    
    
    
class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'account_count' in counters:
            values['account_count'] = request.env['account.account'].search_count([('is_publish', '=', True )])
        return values