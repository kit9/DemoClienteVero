# -*- coding: utf-8 -*-
{
    'name': "Expenses",

    'summary': """
        Trading for each expense in accounting entries.""",

    'description': """
        A merchant is selected in Expenditure and this is recorded in the generated entry
    """,

    'author': "Optimiza",
    'website': "http://grupooptimiza.la",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Expenses',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_expense'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
