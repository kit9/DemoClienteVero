# -*- coding: utf-8 -*-
from odoo import http

# class OptLandedCost(http.Controller):
#     @http.route('/opt_landed_cost/opt_landed_cost/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/opt_landed_cost/opt_landed_cost/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('opt_landed_cost.listing', {
#             'root': '/opt_landed_cost/opt_landed_cost',
#             'objects': http.request.env['opt_landed_cost.opt_landed_cost'].search([]),
#         })

#     @http.route('/opt_landed_cost/opt_landed_cost/objects/<model("opt_landed_cost.opt_landed_cost"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('opt_landed_cost.object', {
#             'object': obj
#         })