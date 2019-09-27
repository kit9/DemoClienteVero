# -*- coding: utf-8 -*-
from odoo import http

# class OptDrowback(http.Controller):
#     @http.route('/opt_drowback/opt_drowback/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/opt_drowback/opt_drowback/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('opt_drowback.listing', {
#             'root': '/opt_drowback/opt_drowback',
#             'objects': http.request.env['opt_drowback.opt_drowback'].search([]),
#         })

#     @http.route('/opt_drowback/opt_drowback/objects/<model("opt_drowback.opt_drowback"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('opt_drowback.object', {
#             'object': obj
#         })