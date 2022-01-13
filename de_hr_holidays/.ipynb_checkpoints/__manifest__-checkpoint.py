# -*- coding: utf-8 -*-
{
    'name': "Dynamic Holidays",

    'summary': """
        Employee Dynamic Holidays
        """,

    'description': """
        Employee Dynamic Holidays
        1- Manager can define holiday dynamically
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Holidays',
    'version': '14.0.0.3',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_holidays','hr_contract','hr_payroll', 'de_employee_shift'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/hr_gazetted_day_wizard.xml',
        'views/hr_shift_schedule_views.xml',
        'views/hr_rest_day_config_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
