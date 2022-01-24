## -*- coding: utf-8 -*-
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
import base64
import ast

def action_check_expense_warning(warning):
    company_info = request.env['res.users'].sudo().search([('id', '=', http.request.env.context.get('uid'))])
    return {
        'warning_message': warning,
        'company_info': company_info
    }

def expense_page_content(flag = 0, expense=0, categ=0, exception=0, subordinate=0, employee=0, warning=0, forcasted=0):
    products = request.env['expense.sub.category'].sudo().search([])       
    is_subordinate_expense = False
    has_subordinate = 0
    employees = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
    if employee !=0:
        employees = request.env['hr.employee'].sudo().search([('id','=',employee)])
    subordinates = request.env['hr.employee'].sudo().search([('expense_incharge_id','=', employees.id)])
    if subordinate != 0:
        is_subordinate_expense = True
        has_subordinate = 1
    sheet_categ= 0
    is_multi_cost_center = False
    is_editable =False
    is_expense_deposit=False
    exception_granted = 'no'
    if exception !=0:
        exception_granted =  'yes'   
    sheet = 0
    if expense != 0:
        sheet = request.env['hr.expense.sheet'].sudo().search([('id','=',expense)])
        sheet_categ = sheet.ora_category_id.id
        if sheet.employee_id.user_id.id==http.request.env.context.get('uid'):
            is_editable =True
        elif sheet.employee_id.expense_incharge_id.user_id.id==http.request.env.context.get('uid'):
            is_editable =True
        managers=sheet.employee_id.parent_id.name
        employees=sheet.employee_id
        if sheet.is_deposit==True:
            is_expense_deposit=True        
    managers = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    contract = request.env['hr.contract'].sudo().search([('employee_id','=', employees.id),('state','=','open')], limit=1)
    cost_center_count = 0
    default_controlled_account = 0
    cost_center_list = []
    cost_center_code_list = []
    default_expense_analytic = 0
    expense_account_head = []
    for cost_center in contract.cost_center_information_line:
        if cost_center.by_default == True:
            default_controlled_account = cost_center.controlled_id.name
        cost_center_list.append(cost_center.cost_center.id)
        cost_center_code_list.append(cost_center.cost_center.code)
        expense_account_head.append(cost_center.controlled_id.id)
        if cost_center.by_default==True:
            default_expense_analytic = cost_center.cost_center.id
        cost_center_count += 1
    if cost_center_count > 1:
        is_multi_cost_center = True
    cost_centers = contract.cost_center_information_line    
    expense_categories = request.env['ora.expense.category'].sudo().search([('company_ids','=', employees.company_id.id)])
    exp_product_list = []
    if categ !=0:
        expense_categories = request.env['ora.expense.category'].sudo().search([('id', '=', categ)])
        products = request.env['expense.sub.category'].sudo().search([('ora_category_id','=', categ)])
    default_analytic = request.env['account.analytic.account'].sudo().search([('id','=', default_expense_analytic)], limit=1)    
    emp_members = request.env['hr.employee.family'].sudo().search([('employee_id','=', employees.id)])
    vehicles = request.env['vehicle.meter.detail'].sudo().search([('id','=',employees.vehicle_id.id)])
    company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
    managers=employees.parent_id.name
    product_list = []
    if exception==0:
        for exist_prod in products:
            for rec in employees.grade_designation.grade_line_ids:
                if exist_prod.id == rec.expense_type.id:
                    product_list.append(exist_prod.id)
        products = request.env['expense.sub.category'].search([('id','in', products.ids)]) 
    controllers = request.env['controlled.account'].search([('id','in', expense_account_head)]) 
    error_flag = '0'
    errora_message = ''
    if warning !=0:
        errora_message = warning
        error_flag = '1'
        
    return {
        'managers': managers,
        'is_editable': is_editable,
        'forcasted': forcasted,
        'employees' : employees,
        'controllers': controllers,
        'default_controlled_account': default_controlled_account,
        'has_subordinate': has_subordinate,
        'error_flag': error_flag,
        'errora_message': errora_message,
        'is_subordinate_expense': is_subordinate_expense,
        'subordinates': subordinates,
        'is_expense_deposit': is_expense_deposit,
        'vehicles': vehicles,
        'default_analytic_name': default_analytic.name,
        'default_analytic': default_analytic,
        'cost_centers': cost_centers,
        'exception': exception_granted,
        'fleets': vehicles,
        'is_multi_cost_center': is_multi_cost_center,
        'is_approval_done': False,
        'products': products,
        'expense': sheet if expense!=0 else 0,
        'emp_members': emp_members,
        'employee_name': employees,
        'expense_types': expense_categories,
        'expense_categories': expense_categories,
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
        
class CreateApproval(http.Controller):
    
    @http.route('/expense/request/category/',type="http", website=True, auth='user')
    def expense_claim_category_template(self, **kw):
        return request.render("de_portal_expence.create_expense_category",expense_page_content())
    
    @http.route('/expense/request/subordinate/',type="http", website=True, auth='user')
    def subordinate_expense_claim_template(self, **kw):
        return request.render("de_portal_expence.create_expense_category",expense_page_content(subordinate=1))
    
    
    @http.route('/expense/category/next/',type="http", website=True, auth='user')
    def expense_claim_create_template(self, **kw):
        categ = int(kw.get('expense_category'))
        exception=0
        employee = 0
        if kw.get('exception'):
            exception=1
        if kw.get('is_subordinate'):    
            if kw.get('employee_id'): 
                employee = int(kw.get('employee_id'))
        else:
            employee = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))]).id
        return request.render("de_portal_expence.create_expense",expense_page_content(categ=categ, exception=exception, employee=employee)) 
    
    
    @http.route('/my/expense/line/save', type="http", auth="public", website=True)
    def create_expenses(self, **kw):
        employee=request.env['hr.employee'].sudo().search([('id','=',int(kw.get('uniq_employee_id')) )], limit=1)
        exception = True if kw.get('ora_exception')=='yes' else False
        ora_category=request.env['ora.expense.category'].sudo().search([('id','=',int(kw.get('ora_category')))], limit=1)
        product = request.env['expense.sub.category'].search([('id','=',int(kw.get('product_id')))], limit=1)
        
        cost_center_count = 0
        forcasted_data = {
            'expense_type': product.id,
            'reference':  kw.get('reference'),
            'unit_amount': kw.get('unit_amount'),
            'product_id': int(kw.get('controll_id')),
            'attachment': kw.get('attachment'),
            'member_id': '0',
            'name': '',
            'fleet_id': 0,
            'meter_reading': 0,
        }
        if kw.get('description'): 
            forcasted_data.update({
                    'name': kw.get('description'),
                }) 
        if kw.get('member_id'): 
            family_member = request.env['hr.employee.family'].search([('id','=', int(kw.get('member_id')))], limit=1)   
            if family_member:
                forcasted_data.update({
                    'member_id': family_member.id,
                })
        if kw.get('fleet_id') : 
            fleet = request.env['vehicle.meter.detail'].search([('id','=',int(kw.get('fleet_id')))], limit=1)           
            if fleet:
                forcasted_data.update({
                    'fleet_id': fleet.id,
                }) 
        if kw.get('meter_reading'):
            forcasted_data.update({
                'meter_reading': kw.get('meter_reading'),
            }) 
        if not kw.get('controll_id'):
            warning_message='You are not allow to Submit Expense Claim! Your Control-Account is not set. Please contact with HR Department.'
            return request.render("de_portal_expence.create_expense",expense_page_content(categ=ora_category.id, exception=exception, employee=employee.id, warning=warning_message, forcasted=forcasted_data))    
        controller = request.env['product.product'].search([('ora_category_id','=', ora_category.id),('controlled_id','=',int(kw.get('controll_id')))], limit=1)
        
        if not kw.get('default_cost_center'):
            warning_message='You are not allow to Submit Expense Claim! Your Default Cost Center is not set. Please contact with HR Department.'
            return request.render("de_portal_expence.create_expense",expense_page_content(categ=ora_category.id, exception=exception, employee=employee.id, warning=warning_message, forcasted=forcasted_data))        
        default_cost_center = int(kw.get('default_cost_center'))
        
        contract = request.env['hr.contract'].sudo().search([('employee_id','=', employee.id),('state','=','open')], limit=1)
        for cost_info in contract.cost_center_information_line:
            cost_center_count += 1
        analytic_vals_list = []
        analytic_cost_list = []
        total_percentage_amount = 0
        if kw.get('cost_center_distrubute'):
            if kw.get('cost_center_distrubute')=='1':
                if kw.get('create_expense_line_vals'):
                    analytic_vals_list = ast.literal_eval(kw.get('create_expense_line_vals'))
                    inner_cost_center_count = 0
                    for analytic_cost in analytic_vals_list:
                        if inner_cost_center_count < (cost_center_count):
                            
                            if analytic_cost['col2'] == '':
                                analytic_cost['col2'] = 0    
                            if int(analytic_cost['col2']) > 0:
                                analytic_account=request.env['account.analytic.account'].sudo().search([                                 
                                ('company_id','=',employee.company_id.id),('name','=',analytic_cost['col1'])], limit=1)
                                total_percentage_amount +=  int(analytic_cost['col2'])
                                analytic_cost_list.append({
                                        'analytic_account': analytic_account.id,
                                        'percentage': int(analytic_cost['col2']),
                                    })
                            inner_cost_center_count += 1    
                    if total_percentage_amount > 100 or total_percentage_amount < 100:
                        warning_message='Your Cost Center Distribution must equal to 100!'    
                        return request.render("de_portal_expence.create_expense",expense_page_content(categ=ora_category.id, exception=exception, employee=employee.id, warning=warning_message, forcasted=forcasted_data))
        if not analytic_cost_list:
            analytic_cost_list.append({
                        'analytic_account': default_cost_center,
                        'percentage': 100,
                    })  
        flag = False
        limit = 0
        period = 0
        ora_unit = 'amount'
        for rec in employee.grade_designation.grade_line_ids:
            if product.id == rec.expense_type.id:
                flag = True
                limit = rec.limit
                ora_unit = rec.ora_unit
                period = int(rec.period)
        expense_period_date = fields.date.today() - relativedelta(years=period)
        if flag == False and exception!=True:
            warning_message="You are not allowed to make Claim against the selected expense type"
            return request.render("de_portal_expence.create_expense",expense_page_content(categ=ora_category.id, exception=exception, employee=employee.id, warning=warning_message, forcasted=forcasted_data))
        else:
            employee_expenses = request.env['hr.expense'].search(
                [('sub_category_id', '=', product.id), ('employee_id', '=', employee.id)
                    , ('state', '!=', 'refused'),
                 ('payment_mode', '=', 'own_account')])
            sum = 0
            for expense in employee_expenses:
                if (expense.create_date.date() > expense_period_date and expense.create_date.date() <= fields.date.today()):
                    sum = sum + expense.total_amount
            sum = round(sum, 2)            
            sum_current = sum + float(kw.get('unit_amount')) 
            if sum_current > limit and product.ora_unit!='km' and exception!=True:
                limit_amount = limit-sum
                warning_message="Already Claimed Amount: " + str(round(sum)) + "\n"+ " Due Amount: " + str(round(limit_amount if limit_amount > 0 else 0)) + "\n" + " Current Amount: "+str(round(float(kw.get('unit_amount')))) + "\n" +" You are not allow to enter amount greater than "+ str(round(limit_amount if limit_amount > 0 else 0))
                return request.render("de_portal_expence.create_expense",expense_page_content(categ=ora_category.id, exception=exception, employee=employee.id, warning=warning_message, forcasted=forcasted_data))    
            else:
                pass   
        if ora_category.is_attachment=='required':
            if not kw.get('attachment'):
                 warning_message='Please Add Attachment! You are not allow to submit '+str(ora_category.name)+ ' Expense claim without attachments.' 
                 return request.render("de_portal_expence.create_expense",expense_page_content(categ=ora_category.id, exception=exception, employee=employee.id, warning=warning_message, forcasted=forcasted_data))
        if not kw.get('fleet_id') and product.ora_unit=='km':
            warning_message='You are not allow to Submit Vehicle Maintenance Expense Claim!'
            return request.render("de_portal_expence.create_expense",expense_page_content(categ=ora_category.id, exception=exception, employee=employee.id, warning=warning_message, forcasted=forcasted_data))
        if kw.get('fleet_id'): 
            fleet = request.env['vehicle.meter.detail'].search([('id','=',int(kw.get('fleet_id')))], limit=1)    
            if fleet:
                if fleet.id!=employee.vehicle_id.id:
                    warning_message='You are not allow to select Vehicle rather than '+str(employee.vehicle_id.name)
                    return request.render("de_portal_expence.create_expense",expense_page_content(categ=ora_category.id, exception=exception, employee=employee.id, warning=warning_message, forcasted=forcasted_data))  
            if kw.get('meter_reading'):
                opening_vehicle_balance = 0
                for reading_line  in employee.vehicle_meter_line_ids:
                    if product.id==reading_line.sub_category_id.id:
                        opening_vehicle_balance = reading_line.opening_reading
                if float(kw.get('meter_reading')) >= 0.0 and product.meter_reading>=0.0:
                    if opening_vehicle_balance <= float(kw.get('meter_reading')):
                        current_reading = float(kw.get('meter_reading')) + opening_vehicle_balance 
                        if exception!=True:
                            if current_reading >= (product.meter_reading+opening_vehicle_balance):
                                pass
                            else:
                                warning_message='Last Reading: ' +str(round(opening_vehicle_balance))+ "\n"+' Due Reading: '+str(round(opening_vehicle_balance+product.meter_reading))+ "\n"+' Current Reading: '+str(round(float(kw.get('meter_reading'))))+ "\n"+' Please Enter Reading Greater than '+str(round(opening_vehicle_balance+product.meter_reading))
                                return request.render("de_portal_expence.create_expense",expense_page_content(categ=ora_category.id, exception=exception, employee=employee.id, warning=warning_message, forcasted=forcasted_data))
                    else:
                        warning_message='Please Enter Reading greater than your last Reading! '+str(opening_vehicle_balance)
                        return request.render("de_portal_expence.create_expense",expense_page_content(categ=ora_category.id, exception=exception, employee=employee.id, warning=warning_message, forcasted=forcasted_data))
        
        exist_sequence=request.env['ir.sequence'].sudo().search([('code','=','expense.sheet.sequence'),('company_id','=', employee.company_id.id)], limit=1)
        if not exist_sequence:
            seq_vals = {
                'name': 'Expense Claim Sequence',
                'code': 'expense.sheet.sequence',
                'implementation': 'standard',
                'number_next_actual': 1,
                'prefix': 'ECV#',
                'company_id': employee.company_id.id,
            }
            exist_sequence= request.env['ir.sequence'].sudo().create(seq_vals) 
        expense_name = request.env['ir.sequence'].sudo().next_by_code('expense.sheet.sequence') or _('New')
        expense_val = {
            'name': expense_name,
            'ora_category_id': int(kw.get('ora_category')),
            'exception':  True if kw.get('ora_exception')=='yes' else False,
            'employee_id': employee.id,
            'accounting_date':  fields.date.today(),
        }
        record = request.env['hr.expense.sheet'].sudo().create(expense_val)
        expense_line = {
                    'name': product.name,
                    'reference': kw.get('reference'),
                    'sheet_id':  record.id,
                    'sub_category_id': product.id,
                    'unit_amount': ((float(kw.get('unit_amount')))),
                    'product_id': int(controller.id),
                    'account_id': controller.property_account_expense_id.id,
                    'analytic_account_id': default_cost_center,
                    'employee_id': employee.id,
                    'date':  fields.date.today(),
        }
        record_line = request.env['hr.expense.sheet.line'].sudo().create(expense_line)
        if kw.get('description'): 
           record_line.update({
                    'name': kw.get('description'),
                }) 
        if kw.get('member_id'): 
            family_member = request.env['hr.employee.family'].search([('id','=', int(kw.get('member_id')))], limit=1)            
            if family_member:
                record_line.update({
                    'member_id': family_member.id,
                })
        if kw.get('fleet_id') : 
            fleet = request.env['vehicle.meter.detail'].search([('id','=',int(kw.get('fleet_id')))], limit=1)            
            if fleet:
                record_line.update({
                    'fleet_id': fleet.id,
                }) 
        if kw.get('meter_reading'):
            record_line.update({
                'meter_reading': kw.get('meter_reading'),
            })

        if kw.get('attachment'):
            Attachments = request.env['ir.attachment']
            name = kw.get('attachment').filename
            file = kw.get('attachment')
            attachment_id = Attachments.sudo().create({
            'name': name,
            'type': 'binary',
            'datas': base64.b64encode(file.read()),
             })
            record_line.update({
                'attachment_id': [(4, attachment_id.id)],
            })
            attachment_id.update({
                'res_model': 'hr.expense.sheet.line',
                'res_id': record_line.id, 
            })

        exist_split_line = 0        
        for analytic_line in analytic_cost_list:
            splitted_line = {
                    'name': product.name,
                    'sub_category_id': product.id,
                    'sheet_line_id': record_line.id,
                    'reference': kw.get('reference'),
                    'sheet_id':  record.id,
                    'unit_amount': ((float(kw.get('unit_amount'))/100)* float(analytic_line['percentage'])),
                    'product_id': int(controller.id),
                    'account_id': controller.property_account_expense_id.id,
                    'analytic_account_id': analytic_line['analytic_account'],
                    'percentage': round(analytic_line['percentage']), 
                    'employee_id': employee.id,
                    'date':  fields.date.today(),
            }
            split_line = request.env['hr.expense'].sudo().create(splitted_line)
            exist_split_line = split_line                        
            if kw.get('description'): 
               split_line.update({
                        'name': kw.get('description'),
                    }) 
            if kw.get('member_id'): 
                family_member = request.env['hr.employee.family'].search([('id','=', int(kw.get('member_id')))], limit=1)            
                if family_member:
                    split_line.update({
                        'member_id': family_member.id,
                    })
            if kw.get('fleet_id') : 
                fleet = request.env['vehicle.meter.detail'].search([('id','=',int(kw.get('fleet_id')))], limit=1)            
                if fleet:
                    split_line.update({
                        'fleet_id': fleet.id,
                    }) 
            if kw.get('meter_reading'):
                split_line.update({
                    'meter_reading': kw.get('meter_reading'),
                })

        if kw.get('attachment') and exist_split_line!=0:

            Attachments = request.env['ir.attachment']
            name = kw.get('attachment').filename
            file = kw.get('attachment')
            attachment_id = Attachments.sudo().create({
            'name': name,
            'type': 'binary',
            'datas': base64.b64encode(file.read()),
             })
            exist_split_line.update({
                'attachment_id': [(4, attachment_id.id)],
            })
            attachment_id.update({
                'res_id': exist_split_line,
                'res_model': 'hr.expense',
                'res_name': exist_split_line.name,
            })
        return request.redirect('/my/expense/%s'%(record.id))
    
    @http.route('/expense/edit/line/save', type="http", auth="public", website=True)
    def create_expenses_lines(self, **kw):
        expense_sheet = request.env['hr.expense.sheet'].sudo().search([('id','=', int(kw.get('expense_id')))], limit=1)
        ora_category=request.env['ora.expense.category'].sudo().search([
                    ('id','=',int(kw.get('ora_category')))], limit=1)
        attachment_docs=kw.get('attachment')
        product = request.env['expense.sub.category'].search([('id','=',int(kw.get('product_id')))], limit=1)
        default_cost_center = int(kw.get('default_cost_center'))
        controller = request.env['product.product'].search([('ora_category_id','=', ora_category.id),('controlled_id','=',int(kw.get('controll_id')))], limit=1)
        cost_center_count = 0
        contract = request.env['hr.contract'].sudo().search([('employee_id','=', expense_sheet.employee_id.id),('state','=','open')], limit=1)
        forcasted_data = {
            'expense_type': product.id,
            'reference':  kw.get('reference'),
            'unit_amount': kw.get('unit_amount'),
            'product_id': int(kw.get('controll_id')),
            'attachment': kw.get('attachment'),
            'member_id': '0',
            'name': '',
            'fleet_id': 0,
            'meter_reading': 0,
        }
        if kw.get('description'): 
            forcasted_data.update({
                    'name': kw.get('description'),
                }) 
        if kw.get('member_id'): 
            family_member = request.env['hr.employee.family'].search([('id','=', int(kw.get('member_id')))], limit=1)   
            if family_member:
                forcasted_data.update({
                    'member_id': family_member.id,
                })
        if kw.get('fleet_id') : 
            fleet = request.env['vehicle.meter.detail'].search([('id','=',int(kw.get('fleet_id')))], limit=1)           
            if fleet:
                forcasted_data.update({
                    'fleet_id': fleet.id,
                }) 
        if kw.get('meter_reading'):
            forcasted_data.update({
                'meter_reading': kw.get('meter_reading'),
            })
            
        for cost_info in contract.cost_center_information_line:
            cost_center_count += 1    
        analytic_vals_list = []
        analytic_cost_list = []
        total_percentage_amount = 0
        if kw.get('cost_center_distrubute'):
            if kw.get('cost_center_distrubute')=='1':
                if kw.get('expense_line_vals'):
                    analytic_vals_list = ast.literal_eval(kw.get('expense_line_vals'))
                    inner_cost_center_count = 0
                    for analytic_cost in analytic_vals_list:
                        if inner_cost_center_count < (cost_center_count):
                            if analytic_cost['col2'] == '':
                                analytic_cost['col2'] = 0
                            if int(analytic_cost['col2']) > 0:
                                analytic_account=request.env['account.analytic.account'].sudo().search([                                     
                                ('company_id','=',expense_sheet.company_id.id),('name','=',analytic_cost['col1'])], limit=1)
                                total_percentage_amount +=  int(analytic_cost['col2'])
                                analytic_cost_list.append({
                                        'analytic_account': analytic_account.id,
                                        'percentage': int(analytic_cost['col2']),
                                    })
                            inner_cost_center_count += 1
                        
                    if total_percentage_amount > 100 or total_percentage_amount < 100:
                        warning_message='Your Cost Center Distribution must equal to 100!'
                        return request.render("de_portal_expence.portal_my_expense", expense_page_content(expense=expense_sheet.id, categ=ora_category.id, exception=expense_sheet.exception, warning=warning_message, forcasted=forcasted_data))
                
        if not analytic_cost_list:
            analytic_cost_list.append({
                        'analytic_account': default_cost_center,
                        'percentage': 100,
                    })  
        flag = False
        limit = 0
        period = 0
        ora_unit = 'amount'
        employee=expense_sheet.employee_id
        for rec in employee.grade_designation.grade_line_ids:
            if product.id == rec.expense_type.id:
                flag = True
                limit = rec.limit
                ora_unit = rec.ora_unit
                period = int(rec.period)
        expense_period_date = fields.date.today() - relativedelta(years=period)
        if flag == False and expense_sheet.exception!=True:
            warning_message="You are not allowed to make Claim against the selected expense type"
            return request.render("de_portal_expence.portal_my_expense", expense_page_content(expense=expense_sheet.id, categ=ora_category.id, exception=exception, warning=warning_message, forcasted=forcasted_data))
        else:
            employee_expenses = request.env['hr.expense'].search(
                [('sub_category_id', '=', product.id), ('employee_id', '=', employee.id)
                    , ('state', '!=', 'refused'),
                 ('payment_mode', '=', 'own_account')])
            sum = 0
            for expense in employee_expenses:
                if (expense.create_date.date() > expense_period_date and expense.create_date.date() <= fields.date.today()):
                    sum = sum + expense.total_amount
            sum = round(sum, 2)        
            sum_current = sum + float(kw.get('unit_amount')) 
            if sum_current > limit and product.ora_unit!='km' and expense_sheet.exception!=True:
                limit_amount = limit-sum
                warning_message="Already Claimed Amount: " + str(sum) + "\n"+ " Due Amount: " + str(round(limit_amount)) + "\n" + " Current Amount: "+str(round(limit_amount if limit_amount > 0 else 0))+ "\n" +" You are not allow to enter amount greater than "+ str(round(limit_amount))
                
                return request.render("de_portal_expence.portal_my_expense", expense_page_content(expense=expense_sudo.id, categ=ora_category.id, exception=expense_sheet.exception, warning=warning_message, forcasted=forcasted_data))
            else:
                pass    
        if expense_sheet.ora_category_id.is_attachment=='required':
            if not kw.get('attachment'):
                 warning_message='Please Add Attachment! You are not allow to submit '+str(expense_sheet.ora_category_id.name)+ ' Expense claim without attachments.' 
                 return request.render("de_portal_expence.portal_my_expense", expense_page_content(expense=expense_sheet.id, categ=ora_category.id, exception=expense_sheet.exception, warning=warning_message, forcasted=forcasted_data))
            
        if kw.get('fleet_id'): 
            fleet = request.env['vehicle.meter.detail'].search([('id','=',int(kw.get('fleet_id')))], limit=1)    
            if fleet:
                if fleet.id!=employee.vehicle_id.id:
                    warning_message='You are not allow to select Vehicle rather than '+str(employee.vehicle_id.name)
                    return request.render("de_portal_expence.portal_my_expense", expense_page_content(expense=expense_sheet.id, categ=ora_category.id, exception=expense_sheet.exception, warning=warning_message, forcasted=forcasted_data))
            if kw.get('meter_reading'):
                opening_vehicle_balance = 0
                for reading_line  in employee.vehicle_meter_line_ids:
                    if product.id==reading_line.sub_category_id.id:
                        opening_vehicle_balance = reading_line.opening_reading
                if float(kw.get('meter_reading')) >= 0.0 and product.meter_reading>=0.0:
                    if opening_vehicle_balance <= float(kw.get('meter_reading')):
                        current_reading = float(kw.get('meter_reading')) + opening_vehicle_balance
                        if expense_sheet.exception!=True:
                            if current_reading >= (product.meter_reading+opening_vehicle_balance):
                                pass
                            else:
                                warning_message='Last Reading: ' +str(round(opening_vehicle_balance))+ "\n" + ' Due Reading: '+str(round(opening_vehicle_balance+product.meter_reading))+ "\n" +' Current Reading: '+str(round(float(kw.get('meter_reading'))))+ "\n"+' Please Enter Reading Greater than '+str(round(opening_vehicle_balance+product.meter_reading))
                                return request.render("de_portal_expence.portal_my_expense", expense_page_content(expense=expense_sheet.id, categ=ora_category.id, exception=expense_sheet.exception, warning=warning_message, forcasted=forcasted_data))
                    else:
                        warning_message='Please Enter Reading greater than your last Reading! '+str(opening_vehicle_balance)
                        return request.render("de_portal_expence.portal_my_expense", expense_page_content(expense=expense_sheet.id, categ=ora_category.id, exception=expense_sheet.exception, warning=warning_message, forcasted=forcasted_data))
        line_vals = {
                    'name': product.name,
                    'reference': kw.get('reference'),
                    'sub_category_id': product.id,
                    'sheet_id':  expense_sheet.id,
                    'unit_amount': ((float(kw.get('unit_amount')))),
                    'product_id': int(controller.id),
                    'account_id': controller.property_account_expense_id.id,
                    'analytic_account_id': default_cost_center,
                    'employee_id': expense_sheet.employee_id.id,
                    'date':  fields.date.today(),
        }
        record_line = request.env['hr.expense.sheet.line'].sudo().create(line_vals)
        if kw.get('description'): 
           record_line.update({
                    'name': kw.get('description'),
                })
        if kw.get('member_id'): 
            family_member = request.env['hr.employee.family'].search([('id','=', int(kw.get('member_id')))], limit=1)            
            if family_member:
                record_line.update({
                    'member_id': family_member.id,
                })

        if kw.get('fleet_id'): 
            fleet = request.env['vehicle.meter.detail'].search([('id','=',int(kw.get('fleet_id')))], limit=1)            
            if fleet:
                record_line.update({
                    'fleet_id': fleet.id,
                }) 
        if kw.get('meter_reading'): 
            record_line.update({
                'meter_reading': kw.get('meter_reading'),
            })
        if attachment_docs:
            Attachments = request.env['ir.attachment']
            name = attachment_docs.filename
            file = attachment_docs
            attachment_id = Attachments.sudo().create({
             'name': name,
             'type': 'binary',
             'datas': base64.b64encode(file.read()),
             })
            record_line.update({
                'attachment_id': [(4, attachment_id.id)],
            }) 
            attachment_id.update({
                'res_model': 'hr.expense.sheet.line',
                'res_id': record_line.id, 
            })
        exist_record_line = 0                            
        for analytic_line in analytic_cost_list:
            split_line_vals = {
                    'name': product.name,
                    'reference': kw.get('reference'),
                    'sheet_line_id': record_line.id,
                    'sub_category_id': product.id,
                    'sheet_id':  expense_sheet.id,
                    'unit_amount': ((float(kw.get('unit_amount'))/100)* float(analytic_line['percentage'])),
                    'product_id': int(controller.id),
                    'account_id': controller.property_account_expense_id.id,
                    'analytic_account_id': analytic_line['analytic_account'],
                    'percentage': round(analytic_line['percentage']), 
                    'employee_id':expense_sheet.employee_id.id,
                    'date':  fields.date.today(),
            }
            split_line = request.env['hr.expense'].sudo().create(split_line_vals)
            exist_record_line =  split_line                       
            if kw.get('description'): 
               split_line.update({
                        'name': kw.get('description'),
                    })
            if kw.get('member_id'): 
                family_member = request.env['hr.employee.family'].search([('id','=', int(kw.get('member_id')))], limit=1)            
                if family_member:
                    split_line.update({
                        'member_id': family_member.id,
                    })

            if kw.get('fleet_id'): 
                fleet = request.env['vehicle.meter.detail'].search([('id','=',int(kw.get('fleet_id')))], limit=1)            
                if fleet:
                    split_line.update({
                        'fleet_id': fleet.id,
                    }) 
            if kw.get('meter_reading'): 
                split_line.update({
                    'meter_reading': kw.get('meter_reading'),
                })
        return request.redirect('/my/expense/%s'%(expense_sheet.id))
       
    

class CustomerPortal(CustomerPortal):
    
    @http.route(['/action/reset/expense/<int:expense_id>'], type='http', auth="public", website=True)
    def action_reset_exepnse_line(self,expense_id , access_token=None, **kw):
        recrd = request.env['hr.expense.sheet'].sudo().browse(expense_id)
        recrd.reset_expense_sheets()
        try:
            expense_sudo = self._document_check_access('hr.expense.sheet', expense_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._expense_get_page_view_values(expense_sudo, **kw) 
        return request.redirect('/my/expense/%s'%(recrd.id)) 
    
    
    @http.route(['/action/vc/approval/<int:expense_id>'], type='http', auth="public", website=True)
    def action_add_vc_approval(self,expense_id , access_token=None, **kw):
        recrd = request.env['hr.expense.sheet'].sudo().browse(expense_id)
        approval = False
        if recrd.employee_id.company_id.chanceller_id:
            for approver in recrd.approval_request_id.approver_ids:
                if approver.user_id.id== recrd.employee_id.company_id.chanceller_id.user_id.id:
                    approval = True
                    break
                else:
                    pass
        if approval==False:
            vals ={
                'user_id': recrd.employee_id.company_id.chanceller_id.user_id.id,
                'request_id': recrd.approval_request_id.id,
                'status': 'new',
            }
            approvers=request.env['approval.approver'].sudo().create(vals)
        values = self._expense_get_page_view_values(recrd, **kw) 
        values.update({
            'is_approval_done': True
        })
        return request.render("de_portal_expence.portal_my_expense", values)
    
    @http.route(['/expense/sheet/line/delete/<int:line_id>'], type='http', auth="public", website=True)
    def action_delete_sheet_expense_line(self,line_id , access_token=None, **kw):
        expense_line = request.env['hr.expense.sheet.line'].sudo().search([('id','=', line_id)], limit=1)
        expense = request.env['hr.expense.sheet'].sudo().search([('id','=', expense_line.sheet_id.id)], limit=1)
        hr_expenses = request.env['hr.expense'].sudo().search([('sheet_line_id','=', expense_line.id)])
        for exp in hr_expenses:
            exp.unlink()
        expense_line.unlink()
            
        exception = 0
        if expense.exception==True:
            exception = 1    
        values = self._expense_get_page_view_values(expense, **kw) 
        return request.render("de_portal_expence.portal_my_expense", expense_page_content(expense=expense.id, categ=expense.ora_category_id.id, exception=exception))
    
    @http.route(['/expense/line/delete/<int:line_id>'], type='http', auth="public", website=True)
    def action_delete_expense_line(self,line_id , access_token=None, **kw):
        expense_line = request.env['hr.expense'].sudo().search([('id','=', line_id)], limit=1)
        expense = request.env['hr.expense.sheet'].sudo().search([('id','=', expense_line.sheet_id.id)], limit=1)
        expense_line.unlink()
        exception = 0
        if expense.exception==True:
            exception = 1    
        values = self._expense_get_page_view_values(expense, **kw) 
        return request.render("de_portal_expence.portal_my_expense", expense_page_content(expense=expense.id, categ=expense.ora_category_id.id, exception=exception))
    
    
    @http.route(['/action/submit/expense/<int:expense_id>'], type='http', auth="public", website=True)
    def action_expense_submit(self,expense_id , access_token=None, **kw):
        recrd = request.env['hr.expense.sheet'].sudo().browse(expense_id)
        recrd.action_submit_sheet()
        try:
            expense_sudo = self._document_check_access('hr.expense.sheet', expense_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._expense_get_page_view_values(expense_sudo, **kw) 
        return request.render("de_portal_expence.portal_my_expense", values)
    
    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'expense_count' in counters:
            values['expense_count'] = request.env['hr.expense'].search_count([('employee_id.user_id', '=', http.request.env.context.get('uid') )])
        return values
  
    def _expense_get_page_view_values(self,expense, access_token = None, **kwargs):
        company_info = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))])
        employee =  request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
        is_expense_deposit = False
        if expense.is_deposit==True:
           is_expense_deposit=True
        values = {
            'page_name' : 'expense',
            'employee_name': employee,
            'is_approval_done': False,
            'is_expense_deposit': is_expense_deposit,
            'managers': employee.parent_id.name,
            'expense' : expense,
            'company_info': company_info,
        }
        return self._get_page_view_values(expense, access_token, values, 'my_expenses_history', False, **kwargs)

    @http.route(['/my/expenses', '/my/expenses/page/<int:page>'], type='http', auth="user", website=True)
    def action_expense_managemment(self, page=1, sortby='name', search='', **kw):
        # only website_designer should access the page Management
        expenses = request.env['hr.expense.sheet']
        employee =  request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
        searchbar_sortings = {
            'ora_category_id': {'label': _('Sort by Category'), 'order': 'ora_category_id'},
            'name': {'label': _('Sort by ECV#'), 'order': 'name'},
            'total_amount': {'label': _('Sort by Amount'), 'order': 'total_amount'},
            'state': {'label': _('Sort by Status'), 'order': 'state'},
        }
        # default sortby order
        sort_order = searchbar_sortings.get(sortby, 'name')['order'] + ', name desc, id'
        expenses = request.env['hr.expense.sheet'].search([('employee_id','=',employee.id)]) 
        subordinates = request.env['hr.employee'].sudo().search([('expense_incharge_id','=', employee.id)]) 
        
        domain = []
        if search:
            domain += ['|','|','|', ('ora_category_id', 'ilike', search), ('name', 'ilike', search), ('total_amount', 'ilike', search),('state', 'ilike', search)]
            
        domain += [('employee_id','=',employee.id)]    
        expenses = expenses.search(domain, order=sort_order)  
               
        expenses_count = len(expenses)
        step = 50
        pager = portal_pager(
            url="/my/expenses",
            url_args={'sortby': sortby},
            total=expenses_count,
            page=expenses,
            step=step
        )
        pages = expenses
        values = {
            'pager': pager,
            'pages': pages,
            'subordinates': subordinates, 
            'expenses': expenses,
            'search': search,
            'sortby': sortby,
            'searchbar_sortings': searchbar_sortings,
        }
        return request.render("de_portal_expence.portal_my_expenses", values)

    
#################################################
#   Subordinate's  Expense Request
#################################################
    
    @http.route(['/subordinate/expenses', '/subordinate/expenses/page/<int:page>'], type='http', auth="user", website=True)
    def action_expense_managemment_subordinate(self, page=1, sortby='name', search='', **kw):
        # only website_designer should access the page Management
        expenses = request.env['hr.expense.sheet']
        employee =  request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))])
        searchbar_sortings = {
            'ora_category_id': {'label': _('Sort by Category'), 'order': 'ora_category_id'},
            'name': {'label': _('Sort by ECV#'), 'order': 'name'},
            'total_amount': {'label': _('Sort by Amount'), 'order': 'total_amount'},
            'state': {'label': _('Sort by Status'), 'order': 'state'},
        }
        # default sortby order
        sort_order = searchbar_sortings.get(sortby, 'name')['order'] + ', name desc, id'
        subordinate_list = request.env['hr.employee'].search([('expense_incharge_id','=',employee.id)])    
        expenses = request.env['hr.expense.sheet'].search([('employee_id','in',subordinate_list.ids)]) 
        subordinates = request.env['hr.employee'].sudo().search([('expense_incharge_id','=', employee.id)]) 
        
        domain = []
        if search:
            domain += ['|','|','|', ('ora_category_id', 'ilike', search), ('name', 'ilike', search), ('total_amount', 'ilike', search),('state', 'ilike', search)]
            
        domain += [('employee_id','in',subordinate_list.ids)]    
        expenses = expenses.search(domain, order=sort_order)          
        expenses_count = len(expenses)
        step = 50
        pager = portal_pager(
            url="/subordinate/expenses",
            url_args={'sortby': sortby},
            total=expenses_count,
            page=expenses,
            step=step
        )
        pages = expenses
        values = {
            'pager': pager,
            'pages': pages,
            'subordinates':subordinates,
            'expenses': expenses,
            'search': search,
            'sortby': sortby,
            'searchbar_sortings': searchbar_sortings,
        }
        return request.render("de_portal_expence.portal_subordinate_expenses", values)

    
   
    @http.route(['/my/expense/<int:expense_id>'], type='http', auth="user", website=True)
    def portal_my_expense(self, expense_id, access_token=None, **kw):
        values = []
        active_user = http.request.env.context.get('uid')
        expense_sudo = request.env['hr.expense.sheet'].sudo().search([('id','=',expense_id)])      
        values = self._expense_get_page_view_values(expense_sudo,access_token, **kw) 
        values.update({
            'expense': expense_sudo,
            'exception':  'Yes' if expense_sudo.exception==True else 'No',
        })
        exception = 0
        if expense_sudo.exception==True:
            exception = 1 
        return request.render("de_portal_expence.portal_my_expense", expense_page_content(expense=expense_sudo.id, categ=expense_sudo.ora_category_id.id, exception=exception))
