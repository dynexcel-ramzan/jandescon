# -*- coding: utf-8 -*-
{
    'name': "Time-Off: Accrual And Pro-rate Allocation",
    'summary': """ Leaves Allocation for Prob Allocated Leaves and Pro Rate
    """,
    'sequence': '1',
    'description': """
    """,
    'category': 'TimeOff',
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    'version': '14.1.0.0',
    'depends': ['base', 'hr_holidays', 'de_employee_enhancement'],
    'data': [
        'data/ir_cron_data.xml',
        'views/hr_employee_view.xml',
        'views/hr_leave_type_view.xml',
    ],
    'demo': [
    ],
    'images': [
    ],
}
