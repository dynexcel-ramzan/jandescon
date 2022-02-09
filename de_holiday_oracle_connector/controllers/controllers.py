# -*- coding: utf-8 -*-
# from odoo import http


# class DeHolidayOracleConnector(http.Controller):
#     @http.route('/de_holiday_oracle_connector/de_holiday_oracle_connector/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_holiday_oracle_connector/de_holiday_oracle_connector/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_holiday_oracle_connector.listing', {
#             'root': '/de_holiday_oracle_connector/de_holiday_oracle_connector',
#             'objects': http.request.env['de_holiday_oracle_connector.de_holiday_oracle_connector'].search([]),
#         })

#     @http.route('/de_holiday_oracle_connector/de_holiday_oracle_connector/objects/<model("de_holiday_oracle_connector.de_holiday_oracle_connector"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_holiday_oracle_connector.object', {
#             'object': obj
#         })
