# -*- coding: utf-8 -*-
{
    'name': "Oracle Attendance Rectification Connector",

    'summary': """
        Oracle Attendance Rectification Connector
        """,

    'description': """
        Oracle Attendance Rectification Connector
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Attendance',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','de_hr_attendance_approvals'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/rectification_server_action.xml',
        'views/rectification_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
