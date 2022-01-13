# -*- coding: utf-8 -*-
{
    'name': "Time Off Type Enhancement",
    'summary': """Given Module Will Provide enhancement in mode (Employee_TYpe) HR Leave Allocation table 
    """,
    'sequence': '2',
    'description': """Assign Leaves According to Employee type by additional Enhancement
    """,
    'category': 'TimeOff',
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    'version': '14.0.0.1',
    'depends': ['base','hr_holidays'],
    'data': [
         'views/allocation_mode_view.xml',
    ],

    'demo': [
    ],
    'images': [],
}
