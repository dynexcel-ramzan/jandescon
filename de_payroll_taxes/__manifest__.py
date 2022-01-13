# -*- coding: utf-8 -*-
{
    'name': "Payroll Taxes",

    'summary': """
        Payroll Income Tax Calculation.
        """,

    'description': """
        Payroll Taxes.
        1-Income Tax Calculation.
        2-Tax Credit.
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Payroll',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll','report_xlsx','de_employee_enhancement'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/hr_tax_credit_report.xml',
        'wizard/hr_tax_credit_wizard.xml',
        'views/fiscal_year_month_views.xml',
        'views/basic_salary_devision_views.xml',
        'views/hr_tax_range_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/salary_adjustment_allowance_views.xml',
        'views/hr_tax_credit_views.xml',
        'views/hr_employee_views.xml', 
        'views/res_company_views.xml',
        'views/tax_credit_type_views.xml',
        'views/hr_salary_rule_category_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_payslip_input_type_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
