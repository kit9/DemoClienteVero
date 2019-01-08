# -*- coding: utf-8 -*-
from odoo import http

# class DetraccionProveedor(http.Controller):
#     @http.route('/detraccion_proveedor/detraccion_proveedor/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/detraccion_proveedor/detraccion_proveedor/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('detraccion_proveedor.listing', {
#             'root': '/detraccion_proveedor/detraccion_proveedor',
#             'objects': http.request.env['detraccion_proveedor.detraccion_proveedor'].search([]),
#         })

#     @http.route('/detraccion_proveedor/detraccion_proveedor/objects/<model("detraccion_proveedor.detraccion_proveedor"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('detraccion_proveedor.object', {
#             'object': obj
#         })