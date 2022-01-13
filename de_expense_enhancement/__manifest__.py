# -*- coding: utf-8 -*-
{
    'name': "Expense Enhancement",
    'summary': """ 
    """,
    'sequence': '2',
    'description': """
    """,
    'category': 'Expenses',
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    'version': '14.0.0.1',
    'depends': ['base','hr_expense'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_enhancement_view.xml',
        'views/hr_employee_enhancement_view.xml',
        'views/grade_designation_line_view.xml',
        'views/hr_expense_enhancement_view.xml',
    ],

    'demo': [
    ],

}
