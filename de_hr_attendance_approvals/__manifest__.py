# -*- coding: utf-8 -*-
{
    'name': "Attendance Approvals",

    'summary': """
        Attendance Rectification and Approvals
        """,

    'description': """
        Attendance Rectification and Approvals
        1- Employee Forget to check in check out  will rectify
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Attendance',
    'version': '14.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','de_oracle_attendance_connector','approvals'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/approval_request_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_attendance_views.xml',
        'views/hr_attendance_rectify_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
