# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product/Material Purchase Requisitions by Employees/Users in odoo',
    'version': '12.0.0.1',
    'category': 'Purchases',
    'summary': 'This plugin helps to manage Purchase Requisition',
    'description': """
    BrowseInfo developed a new odoo/OpenERP module apps.

    Material request is an instruction to procure a certain quantity of materials by purchase , internal transfer or manufacturing.So that goods are available when it require.
    Material request for purchase, internal transfer or manufacturing
    Material request for internal transfer
    Material request for purchase order
    Material request for purchase tender
    Material request for tender
    Material request for manufacturing order.
    product request, subassembly request, raw material request, order request
    manufacturing request, purchase request, purchase tender request, internal transfer request

    
    Material Requisition for purchase, internal transfer or manufacturing
    Material Requisition for internal transfer
    Material Requisition for purchase order
    Material Requisition for purchase tender
    Material Requisition for tender
    Material Requisition for manufacturing order.

    product Requisition for purchase, internal transfer or manufacturing
    product Requisition for internal transfer
    product Requisition for purchase order
    product Requisition for purchase tender
    product Requisition for tender
    product Requisition for manufacturing order.

    product purchase requisition by employee
    product purchase requisition by users

    product purchase requisition for employee
    product purchase requisition for users

    material purchase requisition for employee
    material purchase requisition for users

    material purchase requisition by employee
    material purchase requisition by users
""",
    'author': 'BrowseInfo',
    'price': 39,
    'currency': "EUR",
    #'live_test_url':'https://youtu.be/GnSudPZQIKc',
    'website': 'http://www.browseinfo.in',
    'depends': ['sale_management','purchase','stock','hr'],
    'data': [
            'security/ir.model.access.csv',
            'security/purchase_requisition_security.xml',
            'views/custom_material_view.xml',
            'report/purchase_requisition_report.xml',
            'report/purchase_requisition_report_view.xml',
            'edi/purchase_requisition_template_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
