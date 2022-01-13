# -*- coding: utf-8 -*-
{
    'name': "Auto Employee Appraisal",
    'summary': """ Auto Employee Appraisal """,
    'description': """Auto Employee Appraisal""",
    'sequence': 4,
    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",
    'category': 'inventorty gatepass report',
    'version': '14.0.0.0',
    'depends': ['base','hr_appraisal'],
    
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/auto_employee_cornjob.xml',
        'views/employee_appraisal.xml',
        'views/employee_appraisal_menu.xml',
        
        

    ],
    
}