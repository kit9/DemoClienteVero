# -*- coding: utf-8 -*-
from odoo import http

# class OptExpenses(http.Controller):
#     @http.route('/opt_expenses/opt_expenses/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/opt_expenses/opt_expenses/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('opt_expenses.listing', {
#             'root': '/opt_expenses/opt_expenses',
#             'objects': http.request.env['opt_expenses.opt_expenses'].search([]),
#         })

#     @http.route('/opt_expenses/opt_expenses/objects/<model("opt_expenses.opt_expenses"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('opt_expenses.object', {
#             'object': obj
#         })