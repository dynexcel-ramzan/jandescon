
# -*- coding: utf-8 -*-
{
    'name': "Misc Requests Portal",

    'summary': """
           Employee submit their Misc Requests from portal
           """,

    'description': """
        Employee submit their Misc Requests from portal   
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",
    'category': 'Human Resources',
    'version': '14.0.0.3',

    # any module necessary for this one to work correctly
    'depends': [
        'de_employee_requests', 
        'portal',
        'rating',
        'web',
        'web_tour',
        'digest',
        'base',
       'hr',
                
],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_request_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
#         'demo/demo.xml',
    ],
}








