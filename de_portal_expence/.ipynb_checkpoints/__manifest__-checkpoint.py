# -*- coding: utf-8 -*-
{
    'name': "Portal Expense",

    'summary': """
        Employee  Expense Record From Portal""",

    'description': """
        Employee  Expense Record From Portal
        1- Submit Expense Record From Portal
        2- View Expense Record From Portal
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '14.0.0.2',

    # any module necessary for this one to work correctly
    'depends': [
        'portal',
        'rating',
        'base',
        'resource',
        'web',
        'web_tour',
        'de_payroll_accounting',
        'digest',
        'base',
        'hr_expense', 'hr','de_hr_portal_user','de_expense_enhancement','de_employee_family','de_employee_enhancement'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/product_product_views.xml',
        'views/res_company_views.xml',
        'views/grade_designation_line_views.xml',
        'views/ora_expense_category_views.xml',
        'views/hr_expense_sheet_views.xml',
        'views/hr_employee_views.xml',
        'views/account_move_views.xml',
        'views/hr_expense_views.xml',
        'views/account_account_views.xml',
        'views/portal_expense_templates.xml',
        'views/portal_expense_subordinate_templates.xml',
        'views/vehicle_meter_detail_views.xml',
        'views/account_payment_views.xml',
        'views/expense_sub_category_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
