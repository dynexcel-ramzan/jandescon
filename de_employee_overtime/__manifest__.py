# -*- coding: utf-8 -*-
{
    'name': "HRMS Overtime",

    'summary': """
        Employee overtime request
        """,

    'description': """
        Employee overtime request
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Human Resources',
    'version': '14.0.0.2',
    'depends': ['base' ,'hr', 'hr_contract', 'mail' ,'hr_attendance', 'hr_holidays', 'hr_payroll','de_employee_shift','approvals','de_oracle_attendance_connector'],
    
    'data': [
        'security/security.xml',
        'data/data.xml',
        'data/schedular_action.xml',
        'wizards/hr_overtime_wizards.xml',
        'wizards/overtime_timeoff_wizard.xml',
        'wizards/hr_overtime_allocate_wizards.xml',
        'security/ir.model.access.csv', 
        'views/hr_attendace_views.xml',
        'views/approval_request_views.xml',
        'views/overtime_request_view.xml',
        'views/hr_employee_views.xml',
        'views/hr_overtime_type_view.xml',
        'views/hr_overtime_rule_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_overtime_entry_views.xml',
        'views/hr_work_location_views.xml',
        'views/hr_leave_allocation_views.xml',
    ],
    'demo': [
        'data/hr_overtime_demo.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
}

