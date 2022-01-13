# -*- coding: utf-8 -*-
{
    'name': "Loan Approvals",

    'summary': """
        Employee Loan Request Approvals 
        """,

    'description': """
        Employee Loan Request Approvals
        1- By Using Approval Category
        2- Request Approve by Multiple Approvers
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','approvals','de_employee_loan','de_portal_loan_request'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/approval_request_views.xml',
        'views/hr_loan_views.xml',
        'views/loan_type_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
