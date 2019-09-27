# -*- coding: utf-8 -*-
from odoo import http

# class OptCostManufacturing(http.Controller):
#     @http.route('/opt_cost_manufacturing/opt_cost_manufacturing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/opt_cost_manufacturing/opt_cost_manufacturing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('opt_cost_manufacturing.listing', {
#             'root': '/opt_cost_manufacturing/opt_cost_manufacturing',
#             'objects': http.request.env['opt_cost_manufacturing.opt_cost_manufacturing'].search([]),
#         })

#     @http.route('/opt_cost_manufacturing/opt_cost_manufacturing/objects/<model("opt_cost_manufacturing.opt_cost_manufacturing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('opt_cost_manufacturing.object', {
#             'object': obj
#         })