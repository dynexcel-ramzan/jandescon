# -*- coding: utf-8 -*-
{
    'name': "Recruitment Enhancement",

    'summary': """
        Recruitment Form Enhancement""",

    'description': """
        Recruitment Form Enhancement
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'recruitment',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_recruitment', 'hr_recruitment_survey', 'survey', 'de_employee_enhancement'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizards/recruitment_warning_wizard.xml',
        'security/security.xml',
        'data/data.xml',
        'views/recruitment_enhancement_view.xml',
        'views/recruitment_interview_view.xml',
        'views/recruitment_stages.xml',
        'templates/invite_template.xml',
        'data/sequence.xml',

    ],
    'demo': [
        'data/data.xml',
    ],
}
