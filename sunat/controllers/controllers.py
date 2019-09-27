# -*- coding: utf-8 -*-
from odoo import http
# from werkzeug.datastructures import Headers
# from werkzeug.wrappers import Response
import xlsxwriter
import logging
from odoo.http import request

# from io import BytesIO

_logger = logging.getLogger(__name__)


class Sunat(http.Controller):

    # @http.route('/excel/<int:param>', auth='public')
    # def generar_excel(self, param):
    #     output = BytesIO()
    #     workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    #     worksheet = workbook.add_worksheet()
    #
    #     # Some data we want to write to the worksheet.
    #     expenses = (
    #         ['Rent', 1000],
    #         ['Gas', 100],
    #         ['Food', 300],
    #         ['Gym', 50],
    #     )
    #
    #     _logger.info("Parametro -> " + str(param))
    #
    #     # Start from the first cell. Rows and columns are zero indexed.
    #     row = 0
    #     col = 0
    #
    #     # Iterate over the data and write it out row by row.
    #     for item, cost in (expenses):
    #         worksheet.write(row, col, item)
    #         worksheet.write(row, col + 1, cost)
    #         row += 1
    #
    #     # Write a total using a formula.
    #     worksheet.write(row, 0, 'Total')
    #     worksheet.write(row, 1, '=SUM(B1:B4)')
    #
    #     workbook.close()
    #     output.seek(0)
    #     headers = Headers()
    #     headers.set('Content-Disposition', 'attachment', filename="demo.xlsx")
    #     # return Response('Hello World!')
    #     return Response(output.read(), mimetype='application/vnd.openxmlformats-'
    #                                             'officedocument.spreadsheetml.sheet', headers=headers)

    @http.route('/test', auth='public')
    def sunat_proveedores(self):
        model = request.env['sunat.general_actions'].sudo().search([], limit=1)
        resultado = model.sunat_buen_contribuyente()
        _logger.info(resultado)
        return resultado

    @http.route('/retencion', auth='public')
    def sunat_agente_retencion(self):
        model = request.env['sunat.general_actions'].sudo().search([], limit=1)
        resultado = model.sunat_agente_retencion()
        _logger.info(resultado)
        return resultado

    @http.route('/sunatpersons', auth='public')
    def sunat_agente_retencion(self):
        model = request.env['sunat.general_actions'].sudo().search([], limit=1)
        resultado = model.sunat_create_update_legal_persons()
        _logger.info(resultado)
        return resultado

    @http.route('/percepcion', auth='public')
    def sunat_agente_percepcion(self):
        model = request.env['sunat.general_actions'].sudo().search([], limit=1)
        resultado = model.sunat_agente_percepcion()
        _logger.info(resultado)
        return resultado

    @http.route('/demo', auth='public')
    def obtener_cambio(self):
        model = request.env['sunat.general_actions'].sudo().search([], limit=1)
        cambios = model.get_type_currency()
        _logger.info(cambios)
        return cambios

    @http.route('/reporte', auth='public')
    def reporte(self):
        # registros = request.env['account.move.line'].sudo().search([('account_id.code', 'like', '20111.01')])
        model = request.env['sunat.payment_provider'].sudo().search([], limit=1)
        return model.generate_file()

    @http.route('/secuencia', auth='public')
    def secuencia(self):
        # product_id = self.env.ref('product.product_to_find').id
        sec = request.env['ir.model.data'].xmlid_to_res_id('sunat.seq_sunat_invoice')
        model = request.env['ir.sequence'].browse(sec)
        number = model._next_do()
        model.write({
            'number_next': int(number)
        })
        _logger.info(model.name if model else str(model))
        return str(number)
