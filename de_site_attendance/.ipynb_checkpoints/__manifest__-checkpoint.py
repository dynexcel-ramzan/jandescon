# -*- coding: utf-8 -*-
{
    'name': "Site Attendance",

    'summary': """
             Site Attendance Management 
            """,

    'description': """
             Site Attendance Management 
             1- Configure Site Manager 
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Attendance',
    'version': '14.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_attendance','portal',
        'rating',
        'resource',
         'de_hr_portal_user',
         'de_hr_attendance_approvals',
         'de_employee_overtime',
        'web',
        'web_tour',
         'approvals',       
        'digest',
        'base',
       'hr',],

    # always loaded
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'wizard/site_incharge_wizard.xml',
        'security/security.xml',
        'views/res_company_views.xml',
        'views/approval_request_views.xml',
        'views/site_attendance_view.xml',
        'views/site_attendance_menu.xml',
        'views/site_attendance_template.xml',
        'views/hr_employee_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
