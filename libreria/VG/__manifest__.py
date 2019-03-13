# -*- coding: utf-8 -*-
{
    'name': "Libreria-VG",

    'summary': """
        Informes realizados """,

    'description': """
        Long description of module's purpose
    """,

    'author': "VG",
    'website': "https://www.vallegrande.edu.pe/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'sequence': 0,
    'category': 'base',
    'application': True,
    'version': '1.2',
    'installable': True,
    'auto_install': False,

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'wizard/chart_of_accounts_view.xml',
        #'wizard/record_of_actives_view.xml',
        'wizard/four_retentions_view.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode

}
