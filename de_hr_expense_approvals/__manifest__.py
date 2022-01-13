# -*- coding: utf-8 -*-
{
    'name': "Expense Approvals",
    'summary': """
        HR Expense Approvals
        """,
    'description': """
        HR Expense Approvals
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Human Resource',
    'version': '14.0.0.1',
    'depends': ['base','approvals','hr_expense','de_portal_expence'],
    'data': [
        'data/expense_sequence.xml',
        'security/ir.model.access.csv',
        'views/approval_request_views.xml',
        'views/hr_expense_sheet_views.xml',
    ],
}
