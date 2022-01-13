# -*- coding: utf-8 -*-
{
    'name': "Advance Against Expenses Approvals",

    'summary': """
        Advance Against Expenses Approvals
        """,

    'description': """
        Advance Against Expenses Approvals
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'HR',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','approvals','account', 'hr', 'hr_contract', 'de_expense_advances_portal','analytic'],

    # always loaded
    'data': [
#         'security/ir.model.access.csv',
        'views/approval_request_views.xml',
        'views/expense_advanses_views.xml',
        'views/account_analytic_account_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
#         'demo/demo.xml',
    ],
}
