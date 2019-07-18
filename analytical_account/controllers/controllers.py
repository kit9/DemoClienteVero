# -*- coding: utf-8 -*-
from odoo import http

# class AnalyticalAccount(http.Controller):
#     @http.route('/analytical_account/analytical_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/analytical_account/analytical_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('analytical_account.listing', {
#             'root': '/analytical_account/analytical_account',
#             'objects': http.request.env['analytical_account.analytical_account'].search([]),
#         })

#     @http.route('/analytical_account/analytical_account/objects/<model("analytical_account.analytical_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('analytical_account.object', {
#             'object': obj
#         })