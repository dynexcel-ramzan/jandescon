# -*- coding: utf-8 -*-
{
    'name': "Portal Timesheet",

    'summary': """
        Portal Timesheet Request and print
        """,

    'description': """
        Portal Timesheet Request and print
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'HRMS/Timesheet',
    'version': '14.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_timesheet','approvals','hr','de_employee_enhancement','de_employee_shift', 'web', 'portal','de_portal_approvals'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'report/timesheet_attendance_report.xml',
        'report/timesheet_attendance_report_template.xml',
        'wizard/timesheet_incharge_wizard.xml',
        'views/approval_request_views.xml',
        'views/res_ora_client_views.xml',
        'views/timesheet_attendance_report_views.xml',
        'views/timesheet_attendance_report_template.xml',
        'views/hr_employee_views.xml',
        'views/ora_project_project_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
