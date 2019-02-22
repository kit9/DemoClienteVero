from odoo import models, fields, api
from odoo.exceptions import ValidationError
from io import BytesIO
import xlsxwriter
import base64
import logging

_logger = logging.getLogger(__name__)


class KardexReport(models.TransientModel):
    _name = "sunat.kardex_report"
    _description = "Report Kardex"

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # Data - Jcondori
        lst_move_line = self.env['stock.move.line'].search([('state', 'like', 'done')],
                                                           order="product_id,id")
        # lst_move_line = self.env['account.payment'].search([('type', 'like', 'retencion')])

        # Start from the first cell. Rows and columns are zero indexed.
        row = 0
        col = 0

        worksheet.write(row, col, "ITEM")
        worksheet.write(row, col + 1, "FECHA")
        worksheet.write(row, col + 2, "DOCUMENTO")
        worksheet.write(row, col + 3, "DOCUMENTO")
        worksheet.write(row, col + 4, "DETALLE")
        worksheet.write(row, col + 5, "ENTRADAS")
        worksheet.write(row, col + 6, "ENTRADAS")
        worksheet.write(row, col + 7, "ENTRADAS")
        worksheet.write(row, col + 8, "SALIDAS")
        worksheet.write(row, col + 9, "SALIDAS")
        worksheet.write(row, col + 10, "SALIDAS")
        worksheet.write(row, col + 11, "SALDOS")
        worksheet.write(row, col + 12, "SALDOS")
        worksheet.write(row, col + 13, "SALDOS")
        row += 1

        worksheet.write(row, col + 2, "GUIA")
        worksheet.write(row, col + 3, "FACTURA")
        worksheet.write(row, col + 5, "CANT.")
        worksheet.write(row, col + 6, "P.U.")
        worksheet.write(row, col + 7, "P.T.")
        worksheet.write(row, col + 8, "CANT.")
        worksheet.write(row, col + 9, "P.U.")
        worksheet.write(row, col + 10, "P.T.")
        worksheet.write(row, col + 11, "CANT.")
        worksheet.write(row, col + 12, "P.U.")
        worksheet.write(row, col + 13, "P.T.")
        row += 1

        # Iterador - Jcondori
        for line in lst_move_line:
            # Entrada
            # Cantidad
            in_quantity = 0
            out_quantity = 0
            if "OUT" in line.reference:
                out_quantity = line.qty_done
            else:
                in_quantity = line.qty_done

            # Precio Unitario
            in_price_unit = 0
            out_price_unit = 0
            if line.move_id.sale_line_id or "OUT" in line.reference:
                out_price_unit = line.historical_cost
            else:
                if line.move_id.purchase_line_id:
                    in_price_unit = line.move_id.purchase_line_id.price_unit
                else:
                    # Si es que no tiene compra ni venta
                    in_price_unit = line.product_id.standard_price

            # Totales
            in_total = in_quantity * in_price_unit
            out_total = out_quantity * out_price_unit
            total = line.balance_quantity * line.historical_cost

            # Validaciones de out_price_unit
            if out_price_unit == 0 and out_quantity == 0:
                out_price_unit = ""
                out_total = ""
            if in_price_unit == 0 and in_quantity == 0:
                in_price_unit = ""
                in_total = ""

            # for invoice in payment.invoice_ids:
            # Nombre del Producto
            worksheet.write(row, col + 4, line.product_id.display_name or "")
            # Ingreso
            worksheet.write(row, col + 5, in_quantity or "")
            worksheet.write(row, col + 6, in_price_unit)
            worksheet.write(row, col + 7, in_total)
            # Salidas
            worksheet.write(row, col + 8, out_quantity or "")
            worksheet.write(row, col + 9, out_price_unit)
            worksheet.write(row, col + 10, out_total)
            # Saldo
            worksheet.write(row, col + 11, line.balance_quantity)
            worksheet.write(row, col + 12, line.historical_cost)
            worksheet.write(row, col + 13, total)

            # Extras
            # worksheet.write(row, col + 15, line.reference or "")
            # worksheet.write(row, col + 16, line.balance_quantity)
            # worksheet.write(row, col + 17, line.historical_cost)
            row += 1

        workbook.close()
        output.seek(0)

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(output.getvalue()),
            'txt_filename': "kardex.xlsx"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Report Kardex',
            'res_model': 'sunat.kardex_report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
