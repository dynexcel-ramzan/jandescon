
# -*- coding: utf-8 -*-
{
    'name': "Kiosk Portal",

    'summary': """
           Check-In/Out from portal
           """,

    'description': """
        Employee can Check-In/Out their attendance from portal.   
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",
    'category': 'Human Resources',
    'version': '14.0.0.3',

    # any module necessary for this one to work correctly
    'depends': [ 
        'hr_attendance',
        'portal',
        'rating',
        'web',
        'web_tour',
        'digest',
        'base',
       'hr',
       'de_hr_attendance_approvals',
       'de_oracle_attendance_connector',
                
],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/attendance_kiosk_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
#         'demo/demo.xml',
    ],
}

