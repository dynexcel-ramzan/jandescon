# -*- coding: utf-8 -*-
{
    'name': "Leave Approvals",

    'summary': """
        Leave Approvals
        """,

    'description': """
        Leave Approvals
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Human Resource',
    'version': '14.0.0.2',
    'depends': ['base','hr_holidays' ,'approvals','de_leave_portal'],
    'data': [
        'security/ir.model.access.csv',
        'views/approval_request_views.xml',
        'views/res_company_views.xml', 
        'views/hr_leave_type_views.xml',
        'views/hr_leave_views.xml',
    ],
}
