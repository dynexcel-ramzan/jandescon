# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.



{
    'name': 'Approval Portal',
    'version': '12.0.0.0',
    'category': 'Project',
    'sequence': 10,
    'summary': 'Organize and schedule your Approvals',
    'depends': [
        'approvals',
        'portal',
        'rating',
        'resource',
        'web',
        'web_tour',
        'digest',
        'base',
    ],
    'description': "",
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/approval_web_portal_view.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

