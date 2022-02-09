# -*- coding: utf-8 -*-
{
    'name': "Payroll Batch Report",

    'summary': """
        Payroll Batch Report XLSX
        """,

    'description': """
        Payroll Batch Report XLSX
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Payroll',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll','report_xlsx'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/batch_report.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
