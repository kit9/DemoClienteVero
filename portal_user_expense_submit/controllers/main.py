# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.
from collections import OrderedDict
from odoo import fields, http, _
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.http import request, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        Expense = request.env['hr.expense']
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
        expense_count = Expense.sudo().search_count([('employee_id', '=', employee.id)])
        values.update({
            'expense_count': expense_count,

        })
        return values

    @http.route(['/list/expenses', '/list/expenses/page/<int:page>'], type='http', auth="public", website=True)
    def portal_my_expense(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                          search_in='content', **kw):
        expense = http.request.env['hr.expense']
        domain = []
        values = {}
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)])

        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            domain += search_domain

        domain += ([('employee_id', '=', employee.id)])
        expense_record = request.env['hr.expense'].sudo().search(domain)

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'date desc'},
            'name': {'label': _('Title'), 'order': 'name'},
            'status': {'label': _('Status'), 'order': 'state'},
        }

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }

        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'product_id': {'input': 'product_id', 'label': _('Search in Expense')},
            'date': {'input': 'date', 'label': _('Search in Date')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('product_id', 'all'):
                search_domain = OR([search_domain, [('product_id', 'ilike', search)]])
            if search_in in ('date', 'all'):
                search_domain = OR([search_domain, [('date', 'ilike', search)]])
            domain += search_domain

        expense_count = expense.sudo().search_count([('employee_id', '=', employee.id)])
        pager = portal_pager(
            url="/list/expenses",
            url_args={'sortby': sortby, 'filterby': filterby},
            total=expense_count,
            page=page,
            step=self._items_per_page
        )
        expense = request.env['hr.expense'].sudo().search(domain, order=order, limit=self._items_per_page,
                                                          offset=pager['offset'])

        values.update({
            'date': date_begin,
            'page_name': 'expense',
            'pager': pager,
            'default_url': '/list/expenses',
            'searchbar_sortings': searchbar_sortings,
            'expense_record': expense,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("portal_user_expense_submit.list_expenses", values)

    @http.route(['/create/expense'], type='http', auth='user', website=True)
    def expense(self, redirect=None, date=None, **post):
        values = self._prepare_portal_layout_values()
        values.update({
            'error': {},
            'error_message': [],
        })
        product_name = http.request.env['product.product'].sudo().search([('can_be_expensed', '=', True)])
        unit_price = http.request.env['hr.expense'].sudo().search([])
        employee_name = http.request.env['hr.employee'].sudo().search([])
        paid_name = http.request.env['hr.expense'].sudo().search([])
        date = fields.Date.today()
        currency = request.env.user.partner_id.company_id.currency_id.symbol
        product_uom_id = http.request.env['uom.uom'].sudo().search([])
        analytic_account_id = http.request.env['account.analytic.account'].sudo().search([])

        values.update({
            'redirect': redirect,
            'page_name': 'my_details',
            'product_name': product_name,
            'unit_price': unit_price,
            'employee_name': employee_name,
            'paid_name': paid_name,
            'date': date,
            'currency': currency,
            'product_uom_id': product_uom_id,
            'analytic_account_id': analytic_account_id,
            'fec_hor_viaje': date,
            'fec_viaje': date,
            'hor_ini_viaje': '',
            'centro_costo': '',
            'cc_variable': '',
            'solid_por': '',
            'id_emp_sol': '',
            'divisa': '',
            'precio_total': '',
            'nom_pasajero': '',
            'id_pasajero': '',
            'email_pasajero': '',
            'model_vehiculo': '',
            'punto_salida': '',
            'punto_destino': '',
            'tipo_peticion': '',
            'est_final': '',
            'msg_conductor': '',
            'distr_origen': '',
            'direc_origen': '',
            'distr_destino': '',
            'direc_destino': '',
            'num_vale': '',
        })
        response = request.render("portal_user_expense_submit.submit_expense_details", values)
        return response

    @http.route(['/submit/expense'], type='http', auth="public", website=True)
    def confirm_form(self, **POST):
        values = {
            'name': POST['name'],
            'unit_amount': POST['unit_amount'],
            'quantity': POST['quantity'],
            'product_id': POST['product_id'],
            'employee_id': POST['employee_id'],
            'payment_mode': POST['payment_mode'],
            'date': POST['date'],
            'product_uom_id': POST['product_uom_id'],
            'reference': POST['reference'],
            'analytic_account_id': POST['analytic_account_id'],
            # 'fec_hor_viaje': POST['fec_hor_viaje'],
            # 'fec_viaje': POST['fec_viaje'],
            # 'hor_ini_viaje': POST['hor_ini_viaje'],
            # 'centro_costo': POST['centro_costo'],
            # 'cc_variable': POST['cc_variable'],
            # 'solid_por': POST['solid_por'],
            # 'id_emp_sol': POST['id_emp_sol'],
            # 'divisa': POST['divisa'],
            # 'precio_total': POST['precio_total'],
            # 'nom_pasajero': POST['nom_pasajero'],
            # 'id_pasajero': POST['id_pasajero'],
            # 'email_pasajero': POST['email_pasajero'],
            # 'model_vehiculo': POST['model_vehiculo'],
            # 'punto_salida': POST['punto_salida'],
            # 'punto_destino': POST['punto_destino'],
            # 'tipo_peticion': POST['tipo_peticion'],
            # 'est_final': POST['est_final'],
            # 'msg_conductor': POST['msg_conductor'],
            # 'distr_origen': POST['distr_origen'],
            # 'direc_origen': POST['direc_origen'],
            # 'distr_destino': POST['distr_destino'],
            # 'direc_destino': POST['direc_destino'],
            # 'num_vale': POST['num_vale'],
        }
        expense_obj = request.env['hr.expense']
        expense_id = expense_obj.sudo().create(values)
        attachment_list = request.httprequest.files.getlist('attachment_number')
        for image in attachment_list:
            if POST.get('attachment_number'):
                attachments = {
                    'res_name': image.filename,
                    'res_model': 'hr.expense',
                    'res_id': expense_id.id,
                    'type': 'binary',
                    'datas_fname': image.filename,
                    'name': image.filename,
                }
                attachment_obj = http.request.env['ir.attachment']
                attach = attachment_obj.sudo().create(attachments)
                expense_id.write({'message_main_attachment_id': attach.id})
        values.update({
            'user': request.env.user
        })
        return request.render("portal_user_expense_submit.update_details", values)

    @http.route(['/my/expense/<int:order>'], type='http', auth="public", website=True)
    def my_expense(self, order=None, access_token=None, **kw):
        values = {}
        expense_form = http.request.env['hr.expense']
        values.update({
            'page_name': 'form_expense',
            'expense_form': expense_form.sudo().browse([order]),
        })

        return http.request.render('portal_user_expense_submit.my_view_web', values)

    @http.route(['/my/expense_report/<int:order>'], type='http', auth="user", website=True)
    def expense_print(self, order, **kw):
        pdf, _ = request.env.ref('portal_user_expense_submit.expense_pdf_report').sudo().render_qweb_pdf([order])
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
