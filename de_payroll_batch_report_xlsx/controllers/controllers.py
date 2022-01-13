# -*- coding: utf-8 -*-
# from odoo import http


# class DePayrollBatchReportXlsx(http.Controller):
#     @http.route('/de_payroll_batch_report_xlsx/de_payroll_batch_report_xlsx/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_payroll_batch_report_xlsx/de_payroll_batch_report_xlsx/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_payroll_batch_report_xlsx.listing', {
#             'root': '/de_payroll_batch_report_xlsx/de_payroll_batch_report_xlsx',
#             'objects': http.request.env['de_payroll_batch_report_xlsx.de_payroll_batch_report_xlsx'].search([]),
#         })

#     @http.route('/de_payroll_batch_report_xlsx/de_payroll_batch_report_xlsx/objects/<model("de_payroll_batch_report_xlsx.de_payroll_batch_report_xlsx"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_payroll_batch_report_xlsx.object', {
#             'object': obj
#         })
