{
    "name": "Budget Approvals",
    "category": 'HR',
    "summary": 'Budget Approvals',
    "description": """


    """,
    "sequence": 0,
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    "version": '14.1.0.0',
    "depends": ['base','hr','hr_recruitment','de_recruitment_enhancement'],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizards/budget_approval_wizard.xml',
        'wizards/budget_approval_wizard_new.xml',
        'views/budget_approvals.xml',
        'data/form_name.xml',


    ],

    "price": 25,
    "currency": 'PKR',
    "installable": True,
    "application": True,
    "auto_install": False,
}
