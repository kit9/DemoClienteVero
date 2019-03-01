# -*- coding: utf-8 -*-
{
    'name': "Perzonalizacion",

    'summary': """
        Los procesos que pide sunat el la contabilidad""",

    'description': """
        Se toca temas como la detraccion y la retencion
    """,

    'author': "Optimiza",
    'website': "http://grupooptimiza.la",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'sequence': 1,
    'category': 'Generic Modules/Base',
    'application': True,
    'version': '1.2',
    'installable': True,
    'auto_install': False,

    # any module necessary for this one to work correctly
    'depends': ['sale_management',
                'stock',
                'mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
