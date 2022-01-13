# -*- coding: utf-8 -*-
{
    'name': "Timesheet Workdays",

    'summary': """
        Multiple Timesheet Workdays Request at once""",

    'description': """
        Multiple Timesheet Workdays Request at once
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Timesheet',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_timesheet','de_hr_attendance_approvals','de_oracle_attendance_connector','de_employee_enhancement'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/approval_request_views.xml',
        'views/hr_timesheet_attendance_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
