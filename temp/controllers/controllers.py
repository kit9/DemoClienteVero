# -*- coding: utf-8 -*-
from odoo import http

# class Temp(http.Controller):
#     @http.route('/temp/temp/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/temp/temp/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('temp.listing', {
#             'root': '/temp/temp',
#             'objects': http.request.env['temp.temp'].search([]),
#         })

#     @http.route('/temp/temp/objects/<model("temp.temp"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('temp.object', {
#             'object': obj
#         })