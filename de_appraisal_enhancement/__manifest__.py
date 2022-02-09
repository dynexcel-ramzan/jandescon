# -*- coding: utf-8 -*-
{
    'name': "Appraisal Enhancement",

    'summary': """
        Appraisal enhancement""",

    'description': """
        Appraisal
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'digest', 'hr_appraisal','hr','hr_contract','de_employee_enhancement','de_employee_overtime'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/appraisal_data.xml',
        'views/appraisal_values_views.xml',
        'views/appraisal_views.xml',
        'views/appraisal_objective_views.xml',
        'views/appraisal_feedback_views.xml',

    ],
    # # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
