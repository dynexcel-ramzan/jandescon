# -*- coding: utf-8 -*-
# from odoo import http


# class DeEmployeeBenefits(http.Controller):
#     @http.route('/de_employee_benefits/de_employee_benefits/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_employee_benefits/de_employee_benefits/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_employee_benefits.listing', {
#             'root': '/de_employee_benefits/de_employee_benefits',
#             'objects': http.request.env['de_employee_benefits.de_employee_benefits'].search([]),
#         })

#     @http.route('/de_employee_benefits/de_employee_benefits/objects/<model("de_employee_benefits.de_employee_benefits"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_employee_benefits.object', {
#             'object': obj
#         })
