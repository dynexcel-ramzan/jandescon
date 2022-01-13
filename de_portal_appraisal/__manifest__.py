# -*- coding: utf-8 -*-
{
    'name': "Portal Appraisal",

    'summary': """
        Portal Appraisal
        """,

    'description': """
        Portal Appraisal
        1- Objective.
        2- FeedBack.
        3- Probation.
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Appraisal',
    'version': '14.0.0.3',

    # any module necessary for this one to work correctly
    'depends': ['base','web', 'hr_appraisal','de_hr_portal_user','de_expense_enhancement','de_employee_enhancement','de_appraisal_enhancement'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_appraisal_objective_templates.xml',
        'views/hr_appraisal_improvement_template.xml',
        'views/hr_appraisal_feedback_templates.xml',
        'views/hr_appraisal_probation_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
