# -*- coding: utf-8 -*-
# from odoo import http


# class DeAttendanceAbsentDays(http.Controller):
#     @http.route('/de_attendance_absent_days/de_attendance_absent_days/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_attendance_absent_days/de_attendance_absent_days/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_attendance_absent_days.listing', {
#             'root': '/de_attendance_absent_days/de_attendance_absent_days',
#             'objects': http.request.env['de_attendance_absent_days.de_attendance_absent_days'].search([]),
#         })

#     @http.route('/de_attendance_absent_days/de_attendance_absent_days/objects/<model("de_attendance_absent_days.de_attendance_absent_days"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_attendance_absent_days.object', {
#             'object': obj
#         })
