# -*- coding: utf-8 -*-
from odoo import http

# class Sunat(http.Controller):
#     @http.route('/sunat/sunat/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sunat/sunat/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sunat.listing', {
#             'root': '/sunat/sunat',
#             'objects': http.request.env['sunat.sunat'].search([]),
#         })

#     @http.route('/sunat/sunat/objects/<model("sunat.sunat"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sunat.object', {
#             'object': obj
#         })