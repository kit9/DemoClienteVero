# -*- coding: utf-8 -*-
from odoo import http

# class Detracciones(http.Controller):
#     @http.route('/detracciones/detracciones/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/detracciones/detracciones/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('detracciones.listing', {
#             'root': '/detracciones/detracciones',
#             'objects': http.request.env['detracciones.detracciones'].search([]),
#         })

#     @http.route('/detracciones/detracciones/objects/<model("detracciones.detracciones"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('detracciones.object', {
#             'object': obj
#         })