# -*- coding: utf-8 -*-
{
    'name': "Sunat",

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
    'sequence':0,
    'category': 'Generic Modules/Base',
    'application': True,
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/detraccion.xml',
        'views/document_type.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/menu.xml',
        'data/data_detracciones.xml',
        'data/data_document_type.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}