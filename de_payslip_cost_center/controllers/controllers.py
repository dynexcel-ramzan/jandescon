# -*- coding: utf-8 -*-
# from odoo import http


# class DePayslipCostCenter(http.Controller):
#     @http.route('/de_payslip_cost_center/de_payslip_cost_center/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_payslip_cost_center/de_payslip_cost_center/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_payslip_cost_center.listing', {
#             'root': '/de_payslip_cost_center/de_payslip_cost_center',
#             'objects': http.request.env['de_payslip_cost_center.de_payslip_cost_center'].search([]),
#         })

#     @http.route('/de_payslip_cost_center/de_payslip_cost_center/objects/<model("de_payslip_cost_center.de_payslip_cost_center"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_payslip_cost_center.object', {
#             'object': obj
#         })
