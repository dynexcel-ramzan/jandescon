# -*- coding: utf-8 -*-
# from odoo import http


# class DeHrAttendanceReport(http.Controller):
#     @http.route('/de_hr_attendance_report/de_hr_attendance_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_hr_attendance_report/de_hr_attendance_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_hr_attendance_report.listing', {
#             'root': '/de_hr_attendance_report/de_hr_attendance_report',
#             'objects': http.request.env['de_hr_attendance_report.de_hr_attendance_report'].search([]),
#         })

#     @http.route('/de_hr_attendance_report/de_hr_attendance_report/objects/<model("de_hr_attendance_report.de_hr_attendance_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_hr_attendance_report.object', {
#             'object': obj
#         })
