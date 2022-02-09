# -*- coding: utf-8 -*-
# from odoo import http


# class DeEmployeeOnboardingOffboarding(http.Controller):
#     @http.route('/de_employee_onboarding_offboarding/de_employee_onboarding_offboarding/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_employee_onboarding_offboarding/de_employee_onboarding_offboarding/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_employee_onboarding_offboarding.listing', {
#             'root': '/de_employee_onboarding_offboarding/de_employee_onboarding_offboarding',
#             'objects': http.request.env['de_employee_onboarding_offboarding.de_employee_onboarding_offboarding'].search([]),
#         })

#     @http.route('/de_employee_onboarding_offboarding/de_employee_onboarding_offboarding/objects/<model("de_employee_onboarding_offboarding.de_employee_onboarding_offboarding"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_employee_onboarding_offboarding.object', {
#             'object': obj
#         })
