
# -*- coding: utf-8 -*-
{
    'name': "Activity Portal",

    'summary': """
           Employee submit their activities from portal
           """,

    'description': """
        Employee submit their activities from portal   
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",
    'category': 'Human Resources',
    'version': '14.0.0.3',

    # any module necessary for this one to work correctly
    'depends': [
        'mail', 
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
        'views/activity_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
#         'demo/demo.xml',
    ],
}








