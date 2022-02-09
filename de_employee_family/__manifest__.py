# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name":  "Employee Family Detail",
    "summary":  "Employee Family Details",
    "category":  "Human Resource",
    "description": """""",
    "sequence": 3,
    "author": "Dynexcel",
    "website": "http://www.dynexcel.com",
    "version": '14.0.1.2',
    "depends": ['base', 'hr'],
    "data": [
        'security/ir.model.access.csv',
        'views/employee_family.xml',

    ],
    
    "installable": True,
    "application": False,
    "auto_install": False,
}
