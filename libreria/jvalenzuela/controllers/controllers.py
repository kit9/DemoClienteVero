# -*- coding: utf-8 -*-
from odoo import http

# class Modulo(http.Controller):
#     @http.route('/modulo/modulo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/modulo/modulo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('modulo.listing', {
#             'root': '/modulo/modulo',
#             'objects': http.request.env['modulo.modulo'].search([]),
#         })

#     @http.route('/modulo/modulo/objects/<model("modulo.modulo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('modulo.object', {
#             'object': obj
#         })