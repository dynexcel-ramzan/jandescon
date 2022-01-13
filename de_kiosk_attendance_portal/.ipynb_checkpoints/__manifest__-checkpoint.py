
# -*- coding: utf-8 -*-
{
    'name': "portal Timeoff",

    'summary': """
           Employee submit their leave request from portal
           """,

    'description': """
        Employee submit their leave request from portal   
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '14.0.0.3',

    # any module necessary for this one to work correctly
    'depends': [ 
        'hr_holidays',
        'portal',
        'rating',
        'resource',
        'de_employee_enhancement',
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
        'views/hr_leave_template.xml',
        'views/hr_employee_views.xml',
        'views/hr_leave_type_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
#         'demo/demo.xml',
    ],
}








