# -*- coding: utf-8 -*-
# from odoo import http


# class DeAdvanceSalaryApprovals(http.Controller):
#     @http.route('/de_advance_salary_approvals/de_advance_salary_approvals/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_advance_salary_approvals/de_advance_salary_approvals/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_advance_salary_approvals.listing', {
#             'root': '/de_advance_salary_approvals/de_advance_salary_approvals',
#             'objects': http.request.env['de_advance_salary_approvals.de_advance_salary_approvals'].search([]),
#         })

#     @http.route('/de_advance_salary_approvals/de_advance_salary_approvals/objects/<model("de_advance_salary_approvals.de_advance_salary_approvals"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_advance_salary_approvals.object', {
#             'object': obj
#         })
