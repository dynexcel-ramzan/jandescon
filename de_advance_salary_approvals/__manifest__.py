# -*- coding: utf-8 -*-
{
    'name': "Advance Salary Approvals",

    'summary': """
        Employee Advance Salary Approvals
        """,

    'description': """
        Employee Advance Salary Approvals
        1- Multi level Approval
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_contract', 'de_employee_advance_salary','de_portal_advance_salary_request'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/approval_request_views.xml',
        'views/hr_contract_views.xml',
        'views/salary_advance_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
