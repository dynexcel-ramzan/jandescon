# -*- coding: utf-8 -*-
{
    'name': "WFH Attendance to Oracle",

    'summary': """
        WFH Attendance from ODOO to Oracle""",

    'description': """
        WFH Attendance to Oracle
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Attendance',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_attendance','de_hr_attendance_approvals'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_attendance_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
