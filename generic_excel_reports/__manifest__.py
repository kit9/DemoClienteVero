# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo Dynamic Export Excel Reports For all Application',
    'version': '12.0.0.0',
    'sequence': 4,
    'summary': 'Easy to Export Excel view for all applications i.e CRM,Sales,Purchase,Invoices,Payment,Picking,Customer,Product Etc..',
    'category': 'Extra Tools',
    "price": 30.00,
    "currency": 'EUR',
    'description': """
	BrowseInfo developed a new odoo/OpenERP module apps.
	This module use for 
	-Export data in Excel
	-Global data Export
	-Global Export data for any object.
	-Export Sales Order in Excel, Export Sales data in Excel , Export purchase order in Excel, Export Purchase data in Excel.
	-Export Stock in Excel, Export Product data in Excel, Export Invoice on Excel, Export Product in Excel
	-Dynamic export,export in excel, Excel lead, excel sales order, download sales data, download purchase data, download invoice data
	-BI reporinng
	-Business intelligence, Odoo BI, Accounting Reports
	-XLS reports odoo
	-Odoo xls report
        excel export report on Odoo, Odoo excel export, download excel report, generic export excel report, dynamic excel export report
	reporte de exportacion, تقرير التصدير, Liste exportieren, export rapport, Rapport d'exportation, relatório de exportação, rapporto di esportazione
 
   """,
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'depends': ['base'],
    'data': [	"security/ir.model.access.csv",
		"views/generic_excel_report_view.xml",
        "views/template_view.xml"
             ],
	'qweb': [
		],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.png'],
}
