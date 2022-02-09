# -*- coding: utf-8 -*-
{
    'name': "Employee Reports",

    'summary': """
        Employee Reports
        """,

    'description': """
        Employee Reports
        1- Leave balance report
        2- Employee Hirring Report
        3- Employee Retirement Report
        4- Employee Probation Report
        5- Employee location wise Report
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Employee',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','report_xlsx','hr', 'hr_holidays'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/leave_balance_wizard.xml',
        'wizard/hr_recruitment_wizard.xml',
        'wizard/hr_retirement_wizard.xml',
        'reports/leave_balance_report.xml',
        'reports/hr_recruitment_report.xml',
        'reports/hr_retirement_report.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
