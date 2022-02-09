# -*- coding: utf-8 -*-
# from odoo import http


# class DeTimesheetWorkdays(http.Controller):
#     @http.route('/de_timesheet_workdays/de_timesheet_workdays/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_timesheet_workdays/de_timesheet_workdays/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_timesheet_workdays.listing', {
#             'root': '/de_timesheet_workdays/de_timesheet_workdays',
#             'objects': http.request.env['de_timesheet_workdays.de_timesheet_workdays'].search([]),
#         })

#     @http.route('/de_timesheet_workdays/de_timesheet_workdays/objects/<model("de_timesheet_workdays.de_timesheet_workdays"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_timesheet_workdays.object', {
#             'object': obj
#         })
