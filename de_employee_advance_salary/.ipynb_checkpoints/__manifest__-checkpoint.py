# -*- coding: utf-8 -*-

{
    'name': 'HRMS Advance Salary',
    'version': '14.0.0.1',
    'summary': 'Advance Salary In HR',
    'description': """
        Helps you to manage Advance Salary Request of your company's staff.
        """,
    'category': 'Human Resources',
    'author': "Dynexcel",
    'company': 'Dynexcel',
    'maintainer': 'Dynexcel',
    'website': "https://www.dynexcel.com",
    'depends': [
        'hr_payroll', 'hr', 'account_accountant', 'hr_contract', 'de_employee_loan','de_employee_enhancement',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/salary_structure.xml',
        'views/salary_advance.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

