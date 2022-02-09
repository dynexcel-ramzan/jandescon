# -*- coding: utf-8 -*-
{
    'name': "Payslip Workdays",

    'summary': """
        Payslip workday calculation from attendance and leaves.
        """,

    'description': """
        Payslip workday calculation from attendance and leaves.
        1- Workdays Include  employee shift Attendance.
        2- Workdays Include  employee Leave.
        3- Workdays Include employee Overtime.
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Attendance/Payroll',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll', 'hr_attendance','de_employee_shift', 'de_employee_overtime'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_payslips_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
