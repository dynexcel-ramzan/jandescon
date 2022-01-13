# -*- coding: utf-8 -*-
{
    'name': "Portal Loan Request",

    'summary': """
       Portal User can Submit their Loan Request
        """,

    'description': """
        Advance Salary Request
        1- Portal User can Submit their Loan Request
        2- Loan Request will also generate Approval Request.
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human/Resource',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'de_employee_loan', 'hr','web','de_hr_portal_user'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_loan_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
