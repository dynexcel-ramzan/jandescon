
# -*- coding: utf-8 -*-
{
    'name': "Recruitment Portal",

    'summary': """
           Manage Recruitment Requests from portal
           """,

    'description': """
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",
    'category': 'Human Resources',
    'version': '14.0.0.3',

    # any module necessary for this one to work correctly
    'depends': [ 
        'de_recruitment_enhancement',
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
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_recruitment_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
#         'demo/demo.xml',
    ],
}

