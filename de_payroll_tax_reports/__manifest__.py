# -*- coding: utf-8 -*-
{
    'name': "Payroll Tax Reports",

    'summary': """
        Payroll Tax Reports
        """,

    'description': """
        Payroll Tax Reports
        1- Tax Cartificate.
        2- Tax Computation Report
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Payroll',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll','de_payroll_taxes'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/computation_wizard.xml',
        'wizard/certificate_wizard.xml',
        'reports/tax_computation_report.xml',
        'reports/tax_computation_report_template.xml',
        'reports/tax_certificate_report.xml',
        'reports/tax_certificate_report_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
