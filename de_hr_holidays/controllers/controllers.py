# -*- coding: utf-8 -*-
# from odoo import http


# class DeHrHolidays(http.Controller):
#     @http.route('/de_hr_holidays/de_hr_holidays/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_hr_holidays/de_hr_holidays/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_hr_holidays.listing', {
#             'root': '/de_hr_holidays/de_hr_holidays',
#             'objects': http.request.env['de_hr_holidays.de_hr_holidays'].search([]),
#         })

#     @http.route('/de_hr_holidays/de_hr_holidays/objects/<model("de_hr_holidays.de_hr_holidays"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_hr_holidays.object', {
#             'object': obj
#         })
