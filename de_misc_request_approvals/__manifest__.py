# -*- coding: utf-8 -*-
{
    'name': "Misc Request Approvals",

    'summary': """
        Misc Request Approvals
        """,

    'description': """
        Misc Request Approvals for Misc Requests
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'HR',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','approvals', 'de_employee_requests'],

    # always loaded
    'data': [
#         'security/ir.model.access.csv',
        'views/approval_request_views.xml',
        'views/hr_request_conf_views.xml',
        'views/hr_request_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
#         'demo/demo.xml',
    ],
}
