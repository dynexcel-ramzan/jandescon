# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "PaySlip Salary Report",
    "category": 'HR',
    "summary": "Generate PaySlip Salary Excel Report",
    "description": """
    """,
    "sequence": 1,
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    "version": '14.1.0.0',
    "depends": ['base', 'hr', 'report_xlsx','account','de_base_oracle_connector','de_employee_enhancement','hr_payroll','de_employee_benefits',],
    "data": [
        'reports/payslip_salary_report.xml',
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
