# -*- coding: utf-8 -*-
{
    'name': "Timeoff Oracle Connector",

    'summary': """
        Timeoff Oracle Connector
        1- send leave info
        """,

    'description': """
        Timeoff Oracle Connector
        1- send leave info
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Holidays',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_holidays', 'de_hr_leave_approvals'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/oracle_server_action.xml',
        'views/hr_leave_views.xml',
        'views/res_company_views.xml',
        'views/hr_leave_type_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
