# -- coding: utf-8 --
{
    'name': "Retirement Detail",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/retirement_wizard.xml',
        'report/retirement_detail_report.xml',
        'views/model_view.xml',
        'report/retirement_detail_tem.xml',
        'report/retirement_details_header.xml'

    ],
    # only loaded in demonstration mode
    'application':True,
    'installation':True,
    'auto_install':False,
}