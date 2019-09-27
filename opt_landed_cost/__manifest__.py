# -*- coding: utf-8 -*-
{
    'name': "OPT Landed Costs",

    'summary': """
        Landed Costs
        """,

    'description': """
        Allows you to generate shipping costs for products with average and automatic cost.
    """,

    'author': "Optimiza",
    'website': "http://grupooptimiza.la",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock_landed_costs'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/actios.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
