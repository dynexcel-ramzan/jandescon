# -*- coding: utf-8 -*-
{
    'name': "Oracle Attendance",

    'summary': """
        Oracle Attendance Connector
        """,

    'description': """
        Oracle Attendance Connector
        1-
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Attendance',
    'version': '14.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_attendance','de_employee_enhancement','de_employee_shift'],

    # always loaded
    'data': [
         'data/scheduler_data.xml',
         'security/security.xml',
         'views/hr_user_attendance_views.xml',
         'wizard/hr_attendance_wizard.xml',
        'security/ir.model.access.csv',
        'views/hr_attendance_views.xml',
        'views/hr_employee_views.xml', 
        'views/oracle_setting_connector_views.xml',
         'views/hr_device_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
