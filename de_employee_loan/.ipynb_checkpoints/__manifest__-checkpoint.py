# -*- coding: utf-8 -*-

{
    'name': 'HRMS Loan Management',
    'version': '14.0.0.1',
    'summary': 'Manage Loan Requests',
    'description': """
        Helps you to manage Loan Requests of your company's staff.
        """,
    'category': 'Human Resources',
    'author': "Dynexcel",
    'company': 'Dynexcel',
    'maintainer': 'Dynexcel',
    'website': "https://www.dynexcel.com",
    'depends': [
        'base', 'hr_payroll', 'hr', 'account', 'hr_contract', 'mail', 'de_employee_enhancement'
    ],
    'data': [
        'data/hr_loan_seq.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_loan_views.xml',
        'views/hr_loan_policy_views.xml',
        'views/hr_loan_proof_views.xml',
        'views/hr_loan_type_views.xml',
        'data/salary_rule_loan.xml',
        'views/hr_payroll_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
