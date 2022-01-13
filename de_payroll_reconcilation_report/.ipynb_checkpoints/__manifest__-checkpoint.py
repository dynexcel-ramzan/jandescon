# -*- coding: utf-8 -*-
{
    'name': "Payroll Reconcilation Report",

    'summary': """
        Employee Payroll Reconcilation Report
        """,

    'description': """
        Employee Payroll Reconcilation Report
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Payroll',
    'version': '14.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll', 'de_payroll_taxes'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/reconciliation_wizard.xml',
#         'wizard/reconciliation_detail_wizard.xml',
        'report/reconciliation_report.xml',
        'report/reconciliation_report_template.xml',
        'report/reconciliation_detail_report.xml',
        'report/reconciliation_detail_report_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
