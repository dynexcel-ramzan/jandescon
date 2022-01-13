# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "Employee Promotion",
    "category": 'HR',
    "summary": 'Employee Promotion Summary',
    "description": """
	 
   
    """,
    "sequence": 1,
    "author": "Dynexcel",
    "website": "http://www.dynexcel.com",
    "version": '14.0.0.0',
    "depends": ['hr','base','hr_payroll','de_employee_overtime'],
    "data": [
        'security/ir.model.access.csv',
        'reports/employee_promotion_template.xml',
        'reports/employee_promotion_report.xml',
        'views/employee_promotion_view.xml',
    ],

    "price": 25,
    "currency": 'EUR',
    "installable": True,
    "application": True,
    "auto_install": False,
}