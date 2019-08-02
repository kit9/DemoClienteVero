# -*- coding: utf-8 -*-
from odoo import http

# class OptFatherAccount(http.Controller):
#     @http.route('/opt_father_account/opt_father_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/opt_father_account/opt_father_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('opt_father_account.listing', {
#             'root': '/opt_father_account/opt_father_account',
#             'objects': http.request.env['opt_father_account.opt_father_account'].search([]),
#         })

#     @http.route('/opt_father_account/opt_father_account/objects/<model("opt_father_account.opt_father_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('opt_father_account.object', {
#             'object': obj
#         })