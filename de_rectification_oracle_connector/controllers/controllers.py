# -*- coding: utf-8 -*-
# from odoo import http


# class DeRectificationOracleConnector(http.Controller):
#     @http.route('/de_rectification_oracle_connector/de_rectification_oracle_connector/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_rectification_oracle_connector/de_rectification_oracle_connector/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_rectification_oracle_connector.listing', {
#             'root': '/de_rectification_oracle_connector/de_rectification_oracle_connector',
#             'objects': http.request.env['de_rectification_oracle_connector.de_rectification_oracle_connector'].search([]),
#         })

#     @http.route('/de_rectification_oracle_connector/de_rectification_oracle_connector/objects/<model("de_rectification_oracle_connector.de_rectification_oracle_connector"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_rectification_oracle_connector.object', {
#             'object': obj
#         })
