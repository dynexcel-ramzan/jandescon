# -*- coding: utf-8 -*-
{
    'name': "HRMS Shift",

    'summary': """
           HRMS Shift
           """,

    'description': """
           HRMS Shift
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'HRMS',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr', 'hr_payroll', 'resource','calendar','hr_attendance'],

    # always loaded
    'data': [
        'data/ir_server_actions.xml',
        'views/hr_employee_shift_view.xml',
        'reports/attendance_report_views.xml',
        'security/hr_employee_shift_security.xml',
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/hr_attendance_views.xml',
        'views/shift_gazetted_line_views.xml',
        'views/hr_generate_shift_view.xml',
        'views/hr_shift_schedule_view.xml',
        'views/shift_week_days_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
         'demo/shift_schedule_data.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
}



