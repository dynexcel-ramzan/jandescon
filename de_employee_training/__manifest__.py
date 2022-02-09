# -*- coding: utf-8 -*-
{
    'name': "Employee Training",

    'summary': """
        Employee Training App Modification
    
         """,

    'description': """
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",

    'category': 'Uncategorized',
    'version': '14',

    'depends': ['base','hr','hr_contract'],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/training_view.xml',
        'views/request_view.xml',
        'data/form_name.xml',
        'views/sessions_views.xml',
        'views/employee_training_menu.xml',

    ],
    'images': ['static/description/icon.png'],

}
