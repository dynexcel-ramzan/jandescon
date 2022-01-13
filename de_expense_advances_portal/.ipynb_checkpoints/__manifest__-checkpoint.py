
# -*- coding: utf-8 -*-
{
    'name': "Advance Against Expenses",

    'summary': """
           Submit request for advance against expenses from portal
           """,

    'description': """
        Employee submit request for advance against expenses from portal  
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",
    'category': 'Accounts',
    'version': '14.0.0.3',

    # any module necessary for this one to work correctly
    'depends': [ 
        'account',
        'portal',
        'rating',
        'de_portal_expence',
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
        'data/sequence.xml',
        'views/advance_expense_view.xml',
        'views/expense_advance_template.xml',
        'views/advance_amount_approval_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
#         'demo/demo.xml',
    ],
}








