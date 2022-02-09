# -*- coding: utf-8 -*-
# from odoo import http


# class DePayrollAccounting(http.Controller):
#     @http.route('/de_payroll_accounting/de_payroll_accounting/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_payroll_accounting/de_payroll_accounting/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_payroll_accounting.listing', {
#             'root': '/de_payroll_accounting/de_payroll_accounting',
#             'objects': http.request.env['de_payroll_accounting.de_payroll_accounting'].search([]),
#         })

#     @http.route('/de_payroll_accounting/de_payroll_accounting/objects/<model("de_payroll_accounting.de_payroll_accounting"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_payroll_accounting.object', {
#             'object': obj
#         })
