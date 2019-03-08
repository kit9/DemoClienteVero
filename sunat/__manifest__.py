# -*- coding: utf-8 -*-
{
    'name': "Sunat Peru",

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
    'sequence': 0,
    'category': 'Generic Modules/Base',
    'application': True,
    'version': '1.2',
    'installable': True,
    'auto_install': False,

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'purchase',
        'sale_management',
        'stock',
        'base_automation',
        'account_accountant',
        'odoope_ruc_validation',
        'odoope_currency',
        'uom',
        'sale_stock',
        'purchase_stock',
        'account_asset',
        'hr',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/news/detraccion.xml',
        'views/news/document_type.xml',
        'views/news/customs_code.xml',
        'views/news/classification_goods.xml',
        'views/news/document_type_identity.xml',
        'views/news/Stock_Catalog.xml',
        'views/news/Type_Existence.xml',
        'views/news/Type_Operation.xml',
        'views/account_invoice.xml',
        'views/views.xml',
        'views/templates.xml',
        'wizard/account_bill_txt_view.xml',
        'wizard/withholding_record_view.xml',
        'wizard/kardex_report_view.xml',
        'wizard/inv_perm_val_view.xml',
        'wizard/consolidated_journal_view.xml',
        'wizard/merge_assets_view.xml',
        'views/menu.xml',
        'views/actions.xml',
        'data/data_detracciones.xml',
        'data/customs_code.xml',
        'data/classification_goods.xml',
        'data/document_type.xml',
        'data/document_type_identity.xml',
        'data/Stock_Catalog.xml',
        'data/Type_Existence.xml',
        'data/Type_Operation.xml',
        'data/TypeIncome.xml',
        'data/uom_data.xml',
    ],
}
