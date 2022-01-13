# -*- coding: utf-8 -*-
# from odoo import http


# class DeHrPayrollAccount(http.Controller):
#     @http.route('/de_hr_payroll_account/de_hr_payroll_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_hr_payroll_account/de_hr_payroll_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_hr_payroll_account.listing', {
#             'root': '/de_hr_payroll_account/de_hr_payroll_account',
#             'objects': http.request.env['de_hr_payroll_account.de_hr_payroll_account'].search([]),
#         })

#     @http.route('/de_hr_payroll_account/de_hr_payroll_account/objects/<model("de_hr_payroll_account.de_hr_payroll_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_hr_payroll_account.object', {
#             'object': obj
#         })
