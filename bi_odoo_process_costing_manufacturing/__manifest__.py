# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Manufacturing Process Costing in Odoo',
    'version': '12.0.0.3',
    'category': 'Manufacturing',
    'summary': 'This plugin helps to show process costing on Manufacturing Order based on BOM',
    'description': """
        Process Costing in Manufacturing Order.Configure Direct Material Cost,  Direct Labour Cost,  Direct Overhead Cost, Overhead cost on Bill of Materials.
        Process Costing in Manufacturing Process, Workorder for Manual Assembly - Direct Material Cost, Workorder for Manual Assembly
        Direct material cost on BOM, Direct labour cost on BOM, Overhead cost on BOM
        Direct material cost on Bill of Materials, Direct labour cost on Bill of Materials,  Overhead cost on Bill of Materials.
        Direct material cost on Manufacturing Order, Direct labour cost on Manufacturing Order,  Overhead cost on Manufacturing Order.
        Manufacturing Order with Direct material cost,Manufacturing Order with  Direct labour cost,Manufacturing Order with Overhead cost.  
        - Manufacturing Order with Direct material cost
    - Distributed Direct material cost, Direct labour cost, Overhead cost to Workorders from Manufacturing order when you press create workorder button.
    - Print Process costing report from BOM
    - Print Process costing report from Manufacturing order.
    - Analysis report for Manufacturing process costing.

Calculer le coût de revient dans l'ordre de fabrication. Configurer le coût du matériel direct, le coût de la main-d'œuvre directe, les frais généraux directs, les frais généraux sur la nomenclature.
        Processus d'établissement des coûts dans le processus de fabrication, commande pour l'assemblage manuel - Coût direct du matériel, commande pour l'assemblage manuel
        Coût direct du matériau sur la nomenclature, Coût direct de la main-d'œuvre sur la nomenclature, Coût des frais généraux sur la nomenclature
        Coût direct du matériel sur la nomenclature, Coût direct de la main-d'œuvre sur la nomenclature, Coûts indirects sur la nomenclature.
        Coût direct du matériel sur la commande de fabrication, coût de la main-d'œuvre directe sur la commande de fabrication, frais généraux sur la commande de fabrication.
        Ordre de fabrication avec coût de matériel direct, ordre de fabrication avec coût de main-d'œuvre direct, ordre de fabrication avec frais généraux.
        - Commande de fabrication avec coût matériel direct
    - Coût direct des matériaux distribués, Coût direct de la main d'œuvre, Coût des frais généraux pour les ordres de fabrication à partir de l'ordre de fabrication lorsque vous appuyez sur le bouton Créer un ordre de travail.
    - Impression du rapport d'établissement des coûts du processus à partir de la nomenclature
    - Imprimer le rapport d'établissement des coûts du processus de fabrication.
    - Rapport d'analyse pour l'établissement des coûts des processus de fabrication.

Cálculo de costos de proceso en orden de fabricación. Configuración del costo directo de material, costo directo de mano de obra, costos indirectos, costos generales en la lista de materiales.
        Costo del proceso en el proceso de fabricación, Pedido en serie para el montaje manual - Costo directo del material, Pedido del trabajo para el montaje manual
        Costo directo del material en la lista de materiales, costo directo de mano de obra en la lista de materiales, gastos generales en la lista de materiales
        Costo directo del material en la Lista de materiales, Costo laboral directo en la Lista de materiales, Costo máximo en la Lista de materiales.
        Costo directo del material en Orden de fabricación, Costo laboral directo en Orden de fabricación, Costo aéreo en Orden de fabricación.
        Orden de fabricación con costo material directo, orden de fabricación con costo directo de mano de obra, orden de fabricación con costo adicional.
        - Orden de fabricación con costo material directo
    - Costo de material directo distribuido, Costo de mano de obra directa, Costo general para órdenes de trabajo de Fabricación cuando presiona el botón Crear orden de trabajo.
    - Informe de coste de proceso de impresión de la lista de materiales
    - Imprime el informe de costeo del proceso desde la orden de fabricación.
    - Informe de análisis para el coste del proceso de fabricación.
""",
    'author': 'BrowseInfo',
    'price': 15.00,
    'currency': "EUR",
    'category': 'Manufacturing',
    'live_test_url':'https://youtu.be/GnSudPZQIKc',
    'website': 'http://www.browseinfo.in',
    'depends': ['sale_management','mrp'],
    'data': [
            'security/ir.model.access.csv',
            'views/custom_bom_view.xml',
            'report/mrp_costing_report.xml',
            'report/mrp_bom_report_view.xml',
            'report/mrp_production_report_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
