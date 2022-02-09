# -*- coding: utf-8 -*-
# from odoo import http


# class DeBatchPayslipApprovals(http.Controller):
#     @http.route('/de_batch_payslip_approvals/de_batch_payslip_approvals/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_batch_payslip_approvals/de_batch_payslip_approvals/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_batch_payslip_approvals.listing', {
#             'root': '/de_batch_payslip_approvals/de_batch_payslip_approvals',
#             'objects': http.request.env['de_batch_payslip_approvals.de_batch_payslip_approvals'].search([]),
#         })

#     @http.route('/de_batch_payslip_approvals/de_batch_payslip_approvals/objects/<model("de_batch_payslip_approvals.de_batch_payslip_approvals"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_batch_payslip_approvals.object', {
#             'object': obj
#         })
