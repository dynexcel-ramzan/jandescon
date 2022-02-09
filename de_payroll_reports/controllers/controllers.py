# -*- coding: utf-8 -*-
# from odoo import http


# class DePayrollReports(http.Controller):
#     @http.route('/de_payroll_reports/de_payroll_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_payroll_reports/de_payroll_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_payroll_reports.listing', {
#             'root': '/de_payroll_reports/de_payroll_reports',
#             'objects': http.request.env['de_payroll_reports.de_payroll_reports'].search([]),
#         })

#     @http.route('/de_payroll_reports/de_payroll_reports/objects/<model("de_payroll_reports.de_payroll_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_payroll_reports.object', {
#             'object': obj
#         })
