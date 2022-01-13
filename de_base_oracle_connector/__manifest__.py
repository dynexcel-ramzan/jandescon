# -*- coding: utf-8 -*-
{
    'name': "Oracle Connector",

    'summary': """
        Oracle Database Connector""",

    'description': """
        Connect Oracle Database with ODOO
        1- send journal items from odoo to oracle       
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Oracle',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account','analytic','hr'],
    #'external_dependencies': {'python': ['cx_Oracle']},
   

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/oracle_instance_setting_views.xml',
        'views/res_company_views.xml',
        'views/account_move_views.xml',
        'views/account_account_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
