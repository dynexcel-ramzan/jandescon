# -*- coding: utf-8 -*-
# from odoo import http


# class DeHrPayrollEmployeeRules(http.Controller):
#     @http.route('/de_hr_payroll_employee_rules/de_hr_payroll_employee_rules/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_hr_payroll_employee_rules/de_hr_payroll_employee_rules/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_hr_payroll_employee_rules.listing', {
#             'root': '/de_hr_payroll_employee_rules/de_hr_payroll_employee_rules',
#             'objects': http.request.env['de_hr_payroll_employee_rules.de_hr_payroll_employee_rules'].search([]),
#         })

#     @http.route('/de_hr_payroll_employee_rules/de_hr_payroll_employee_rules/objects/<model("de_hr_payroll_employee_rules.de_hr_payroll_employee_rules"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_hr_payroll_employee_rules.object', {
#             'object': obj
#         })
