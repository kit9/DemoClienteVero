# -*- coding: utf-8 -*-
{
    'name': "Gestión de Colas",

    'summary': """
        Colas de Tickes y calculo del fin de la atención""",

    'description': """
        Poder Gestionar el orden de atencion de los tickets de soporte
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'sequence': 0,
    'category': 'Generic Modules/Base',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base', 'helpdesk'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/inherits.xml',
        'views/helpdesk.xml',
        'views/helpdesk.queue_management.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
