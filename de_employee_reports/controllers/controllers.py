# -*- coding: utf-8 -*-
# from odoo import http


# class DeEmployeeReports(http.Controller):
#     @http.route('/de_employee_reports/de_employee_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_employee_reports/de_employee_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_employee_reports.listing', {
#             'root': '/de_employee_reports/de_employee_reports',
#             'objects': http.request.env['de_employee_reports.de_employee_reports'].search([]),
#         })

#     @http.route('/de_employee_reports/de_employee_reports/objects/<model("de_employee_reports.de_employee_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_employee_reports.object', {
#             'object': obj
#         })
