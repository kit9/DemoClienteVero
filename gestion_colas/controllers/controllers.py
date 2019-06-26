# -*- coding: utf-8 -*-
import pytz
import logging
from odoo.http import request
from odoo import http, fields
from datetime import datetime, timedelta
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal

_logger = logging.getLogger(__name__)


# class CustomerPortal(CustomerPortal):
# @http.route([
#     "/helpdesk/ticket/<int:ticket_id>",
#     "/helpdesk/ticket/<int:ticket_id>/<token>",
#     '/my/ticket/<int:ticket_id>'
# ], type='http', auth="public", website=True)
# def tickets_followup(self, ticket_id=None, access_token=None, **kw):
#     try:
#         ticket_sudo = self._document_check_access('helpdesk.ticket', ticket_id, access_token)
#     except (AccessError, MissingError):
#         return request.redirect('/my')
#
#     values = self._ticket_get_page_view_values(ticket_sudo, access_token, **kw)
#
#     values.update({
#         'msg': observacion
#     })
#     return request.render("helpdesk.tickets_followup", values)

# @http.route([
#     "/helpdesk/ticket/<int:ticket_id>",
#     "/helpdesk/ticket/<int:ticket_id>/<token>",
#     '/my/ticket/<int:ticket_id>'
# ], type='http', auth="public", website=True)
# def tickets_followup(self, ticket_id=None, access_token=None, **kw):
#     res = super(CustomerPortal, self).tickets_followup()
#     # Your code goes here
#     _logger.info("Controlador heredado")
#     res.values.update({
#         'atencion': observacion
#     })
#     return res


class GestionColas(http.Controller):

    @http.route('/colas', auth='public')
    def colas(self):
        model = request.env['resource.calendar'].browse(4)

        datetime_now = fields.Datetime.now()

        # _logger.info(model.name)
        _logger.info(datetime.now())
        # _logger.info(fields.Datetime.now())
        queue_ana_vals = {
            'name': "Codigo2",
            'helpdesk_ticket_id': False,
            'start_datetime': datetime_now,
            'duration': 1,
            'is_analysis': True,
        }

        horas = model.plan_hours(6, datetime_now)
        _logger.info("------------------------- horas --------------------------------")
        _logger.info("Inicio -> " + str(datetime_now))
        _logger.info("Fin    -> " + str(horas))

        return "Todo bien"

    @http.route('/last', auth='public')
    def last_registry(self):
        timezone = pytz.timezone('America/Lima')
        model = request.env['helpdesk.queue_management']
        response = ""
        datetime_now = datetime.now()
        time = datetime_now.strftime("%Y-%m-%d %I:%M:%S")
        _logger.info(datetime_now.strftime("%d/%m/%Y %I:%M:%S %p"))
        domain = [  # ('start_datetime', '>=', time)
            # , ('end_datetime', '<=', time)
        ]
        _logger.info(domain)
        models = model.search(domain)
        models = models.filtered(lambda r: r.start_datetime <= datetime_now and r.end_datetime >= datetime_now)
        for model in models:
            _logger.info(model.start_datetime.strftime("%Y-%m-%d %I:%M:%S"))
            _logger.info(model.start_datetime.strftime("%d/%m/%Y %I:%M:%S %p"))
            response = response + \
                       str(model.id) + "," + \
                       str(model.name) + "," + \
                       str(model.start_datetime.strftime("%d/%m/%Y %I:%M:%S %p")) + "," + \
                       str(model.end_datetime.strftime("%d/%m/%Y %I:%M:%S %p")) + \
                       str(model.user_id.id) + "," + \
                       "<br/>"  # +"\r\n"

        # Crear un Tiempo
        # queue_vals = {
        #     'name': "Codigo2",
        #     'helpdesk_ticket_id': False,
        #     'start_datetime': datetime_now,
        #     'duration': 1,
        #     'is_analysis': True,
        # }
        # object = model.create(queue_vals)

        return response

    @http.route('/hour', auth='public')
    def hour_work(self):
        timezone = pytz.timezone('America/Lima')
        model = request.env['helpdesk.queue_management']
        response = ""

        datetime_now = datetime.now()
        return response
