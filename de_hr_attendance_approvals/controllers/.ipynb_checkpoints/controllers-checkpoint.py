# -*- coding: utf-8 -*-
# from odoo import http


# class DeHrAttendanceApprovals(http.Controller):
#     @http.route('/de_hr_attendance_approvals/de_hr_attendance_approvals/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_hr_attendance_approvals/de_hr_attendance_approvals/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_hr_attendance_approvals.listing', {
#             'root': '/de_hr_attendance_approvals/de_hr_attendance_approvals',
#             'objects': http.request.env['de_hr_attendance_approvals.de_hr_attendance_approvals'].search([]),
#         })

#     @http.route('/de_hr_attendance_approvals/de_hr_attendance_approvals/objects/<model("de_hr_attendance_approvals.de_hr_attendance_approvals"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_hr_attendance_approvals.object', {
#             'object': obj
#         })
