
# -*- coding: utf-8 -*-
{
    'name': "Training Requests Portal",

    'summary': """
           Employee submit their training request from portal
           """,

    'description': """
        Employee submit their training request from portal   
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [ 
        'portal',
        'rating',
        'de_employee_training',
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
        'views/training_request_portal.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
#         'demo/demo.xml',
    ],
}

