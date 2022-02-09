# -*- coding: utf-8 -*-
{
    'name': "Portal Advance Salary Request",

    'summary': """
       Portal User can Submit their Advance Salary Request
        """,

    'description': """
        Advance Salary Request
        1- Portal User can Submit their Advance Salary Request
        2- Advance Salary Request will also generate Approval Request.
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human/Resource',
    'version': '14.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'de_employee_advance_salary', 'hr','web','de_hr_portal_user'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/advance_salary_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
