# -*- coding: utf-8 -*-
# from odoo import http


# class DeApprisalObjectiveReport(http.Controller):
#     @http.route('/de_apprisal_objective_report/de_apprisal_objective_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_apprisal_objective_report/de_apprisal_objective_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_apprisal_objective_report.listing', {
#             'root': '/de_apprisal_objective_report/de_apprisal_objective_report',
#             'objects': http.request.env['de_apprisal_objective_report.de_apprisal_objective_report'].search([]),
#         })

#     @http.route('/de_apprisal_objective_report/de_apprisal_objective_report/objects/<model("de_apprisal_objective_report.de_apprisal_objective_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_apprisal_objective_report.object', {
#             'object': obj
#         })
