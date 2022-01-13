# -*- coding: utf-8 -*-
# from odoo import http


# class DeWfhAttendanceConnector(http.Controller):
#     @http.route('/de_wfh_attendance_connector/de_wfh_attendance_connector/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_wfh_attendance_connector/de_wfh_attendance_connector/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_wfh_attendance_connector.listing', {
#             'root': '/de_wfh_attendance_connector/de_wfh_attendance_connector',
#             'objects': http.request.env['de_wfh_attendance_connector.de_wfh_attendance_connector'].search([]),
#         })

#     @http.route('/de_wfh_attendance_connector/de_wfh_attendance_connector/objects/<model("de_wfh_attendance_connector.de_wfh_attendance_connector"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_wfh_attendance_connector.object', {
#             'object': obj
#         })
