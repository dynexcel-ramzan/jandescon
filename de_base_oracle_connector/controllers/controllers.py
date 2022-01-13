# -*- coding: utf-8 -*-
# from odoo import http


# class DeShiftAttendance(http.Controller):
#     @http.route('/de_shift_attendance/de_shift_attendance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_shift_attendance/de_shift_attendance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_shift_attendance.listing', {
#             'root': '/de_shift_attendance/de_shift_attendance',
#             'objects': http.request.env['de_shift_attendance.de_shift_attendance'].search([]),
#         })

#     @http.route('/de_shift_attendance/de_shift_attendance/objects/<model("de_shift_attendance.de_shift_attendance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_shift_attendance.object', {
#             'object': obj
#         })
