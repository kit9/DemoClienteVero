# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.
from collections import OrderedDict
from odoo import fields, http, _
from odoo.exceptions import AccessError
from odoo.http import request, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        expense_sheet = request.env['hr.expense.sheet']
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
        expense_sheet_count = expense_sheet.sudo().search_count([('employee_id', '=', employee.id)])
        values.update({
            'expense_sheet_count': expense_sheet_count,

        })
        return values

    @http.route(['/expence_sheet/list/expenses', '/expence_sheet/list/expenses/page/<int:page>'], type='http',
                auth="public", website=True)
    def portal_expense_sheet(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                             search_in='content', **kw):
        expenses_sheet = request.env['hr.expense.sheet']
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
        expense_sheet_record = request.env['hr.expense.sheet'].sudo().search(domain)
        searchbar_sortings = {
            'accounting_date': {'label': _('Newest'), 'order': 'accounting_date desc'},
            'name': {'label': _('Title'), 'order': 'name'},
            'status': {'label': _('Status'), 'order': 'state'},
        }

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }

        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'employee_id': {'input': 'employee_id', 'label': _('Search in Employee')},
            'accounting_date': {'input': 'accounting_date', 'label': _('Search in Date')},
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
            if search_in in ('employee_id', 'all'):
                search_domain = OR([search_domain, [('employee_id', 'ilike', search)]])
            if search_in in ('accounting_date', 'all'):
                search_domain = OR([search_domain, [('accounting_date', 'ilike', search)]])
            domain += search_domain

        expense_sheet_count = expenses_sheet.sudo().search_count([('employee_id', '=', employee.id)])
        pager = portal_pager(
            url="/expence_sheet/list/expenses",
            url_args={'sortby': sortby, 'filterby': filterby},
            total=expense_sheet_count,
            page=page,
            step=self._items_per_page
        )
        expenses_sheet = request.env['hr.expense.sheet'].sudo().search(domain, order=order, limit=self._items_per_page,
                                                                       offset=pager['offset'])

        values.update({
            'date': date_begin,
            'page_name': 'expenses_sheet',
            'pager': pager,
            'default_url': '/expence_sheet/list/expenses',
            'searchbar_sortings': searchbar_sortings,
            'expense_sheet_record': expenses_sheet,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("portal_user_expense_submit.list_expenses_sheet", values)

    @http.route(['/my/expense_sheet_form/<int:order>'], type='http', auth="public", website=True)
    def my_sheet_expense(self, order=None, **kw):
        values = {}
        expense_sheet_form = http.request.env['hr.expense.sheet']
        values.update({
            'page_name': 'form_expense',
            'expense_sheet_form': expense_sheet_form.sudo().browse([order]),
        })

        return http.request.render('portal_user_expense_submit.expences_sheet_form_view', values)

    @http.route(['/my/expense_sheet/<int:order>'], type='http', auth="user", website=True)
    def expense_sheet_print(self, order, **kw):
        pdf, _ = request.env.ref('hr_expense.action_report_hr_expense_sheet').sudo().render_qweb_pdf([order])
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
