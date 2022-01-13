# -*- coding: utf-8 -*-
{
    'name': "Payroll Accounting",

    'summary': """
        Payroll Accounting
        """,

    'description': """
        Payroll Accounting
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Payroll',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll', 'account', 'de_employee_enhancement'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_account_views.xml',
        'views/controlled_account_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
