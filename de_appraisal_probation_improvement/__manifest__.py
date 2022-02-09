# -*- coding: utf-8 -*-
{
    'name': "de_appraisal_probation_improvement",

    'summary': """
    """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Dynexcel",
    'website': "dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Appraisal',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr'],

    # always loaded
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/hr_appraisal_probation_view.xml',
        'views/hr_appraisal_improvement_view.xml',
#         'views/menu_items_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
