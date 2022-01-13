# -*- coding: utf-8 -*-
# from odoo import http


# class DeAppraisalProbationImprovement(http.Controller):
#     @http.route('/de_appraisal_probation_improvement/de_appraisal_probation_improvement/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_appraisal_probation_improvement/de_appraisal_probation_improvement/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_appraisal_probation_improvement.listing', {
#             'root': '/de_appraisal_probation_improvement/de_appraisal_probation_improvement',
#             'objects': http.request.env['de_appraisal_probation_improvement.de_appraisal_probation_improvement'].search([]),
#         })

#     @http.route('/de_appraisal_probation_improvement/de_appraisal_probation_improvement/objects/<model("de_appraisal_probation_improvement.de_appraisal_probation_improvement"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_appraisal_probation_improvement.object', {
#             'object': obj
#         })
