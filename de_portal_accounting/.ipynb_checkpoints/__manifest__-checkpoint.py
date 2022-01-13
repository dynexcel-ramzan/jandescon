# -*- coding: utf-8 -*-
{
    'name': "Account Entry",

    'summary': """
        Employee Portal Account Entry 
        """,

    'description': """
        Employee Portal Account Entry 
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','web','account_accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/account_account_views.xml',
        'views/portal_account_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
