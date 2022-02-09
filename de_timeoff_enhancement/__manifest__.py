# -*- coding: utf-8 -*-
{
    'name': "Time Off Enhancement",
    'summary': """Given Module Will Provide enhancement in Time Off MGMT in HR 
    """,
    'sequence': '2',
    'description': """Managing Employee's Leaves Automatically allocated
    """,
    'category': 'TimeOff',
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    'version': '14.0.0.1',
    'depends': ['base','hr_holidays','de_timeoff_type','de_employee_overtime', 'de_hr_leave_approvals','de_employee_enhancement'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/automatic_allocation_view.xml',
        'views/hr_leave_type_views.xml',
        'views/hr_leave_allocation_enhance_view.xml',
        'views/hr_leave_view.xml',
        #'views/fiscal_year_view.xml',
    ],

    'demo': [
    ],
    'images': ['static/description/main_screenshot.png'],
}
