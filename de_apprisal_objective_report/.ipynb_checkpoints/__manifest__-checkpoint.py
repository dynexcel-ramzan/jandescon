# -*- coding: utf-8 -*-
{
    'name': "Objective Setting Report",

    'summary': """
        Objective Setting Report
        
        """,

    'description': """
        Objective Setting Report
        1- Excel
        2- Check Objective Status 
        3- By Department Wise
        4- By Location Wise
        5- By Company Wise
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'HRMS/Appraisal',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','de_appraisal_enhancement',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/objective_setting_report.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}


