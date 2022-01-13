# -*- coding: utf-8 -*-
{
    'name': "Attendane Absent Report",

    'summary': """
        Print Attendane Absent Report in Excel
        """,

    'description': """
        Print Attendane Absent Report in Excel
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Attendance',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','report_xlsx','hr_attendance','de_employee_shift', 'de_employee_enhancement'],

    # always loaded
    'data': [ 
        'security/ir.model.access.csv',
        'wizard/absent_report_wizard.xml',
        'report/absent_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installation': True,
    'auto_install': False,
}
