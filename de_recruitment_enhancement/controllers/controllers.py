# -*- coding: utf-8 -*-
# from odoo import http


# class DeRecruitmentEnhancement(http.Controller):
#     @http.route('/de_recruitment_enhancement/de_recruitment_enhancement/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_recruitment_enhancement/de_recruitment_enhancement/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_recruitment_enhancement.listing', {
#             'root': '/de_recruitment_enhancement/de_recruitment_enhancement',
#             'objects': http.request.env['de_recruitment_enhancement.de_recruitment_enhancement'].search([]),
#         })

#     @http.route('/de_recruitment_enhancement/de_recruitment_enhancement/objects/<model("de_recruitment_enhancement.de_recruitment_enhancement"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_recruitment_enhancement.object', {
#             'object': obj
#         })
