# -*- coding: utf-8 -*-
{
    'name': "Employee Requests",

    'summary': """
        Employee Request App 
    
         """,

    'description': """
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",

    'category': 'Employee',
    'version': '14',

    'depends': ['base', 'hr', 'de_employee_enhancement'],

    'data': [
        'security/ir.model.access.csv',
        'data/form_name.xml',
        'security/security.xml',
        'views/hr_request_config_view.xml',
        'views/hr_request_view.xml',
        'views/hr_request_menu.xml',
        # 'views/request_view.xml',
        # 'views/sessions_views.xml',
        # 'views/employee_training_menu.xml',

    ],
    'images': ['static/description/form-icon.png'],
    "application": True,

}
