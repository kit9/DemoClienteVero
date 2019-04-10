from odoo import models, fields, api
from odoo.exceptions import ValidationError
from io import BytesIO
import xlsxwriter
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class KardexReport(models.TransientModel):
    _name = "sunat.kardex_report"
    _description = "Report Kardex"

    date_month = fields.Char(string="Mes", size=2)
    date_year = fields.Char(string="Año", size=4)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        dominio = [('state', 'like', 'done'),
                   ('month_year_inv', 'like', self.date_month + "" + self.date_year)]

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # Data
        lst_move_line = self.env['stock.move.line'].search(dominio, order="product_id,id")

        # Start from the first cell. Rows and columns are zero indexed.
        row = 0
        col = 0

        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'text_wrap': 1, 'valign': 'top', 'bold': True, 'border': 1})
        border = workbook.add_format({'text_wrap': 1, 'border': 1})

        worksheet.write(row, col + 0, "Periodo", bold)
        worksheet.write(row, col + 1, "CUO", bold)
        worksheet.write(row, col + 2, "Correlativo del Asiento", bold)
        worksheet.write(row, col + 3, "Código de establecimiento anexo:", bold)
        worksheet.write(row, col + 4, "Código del catálogo utilizado", bold)
        worksheet.write(row, col + 5, "Tipo de existencia", bold)
        worksheet.write(row, col + 6, "Código propio de la existencia", bold)
        worksheet.write(row, col + 7, "Código de la existencia", bold)
        worksheet.write(row, col + 8, "Fecha de emisión del documento de traslado", bold)
        worksheet.write(row, col + 9, "Tipo del documento de traslado", bold)
        worksheet.write(row, col + 10, "Número de serie del documento de traslado", bold)
        worksheet.write(row, col + 11, "Número del documento de traslado", bold)
        worksheet.write(row, col + 12, "Tipo de operación efectuada", bold)
        worksheet.write(row, col + 13, "Descripción de la existencia", bold)
        worksheet.write(row, col + 14, "Código de la unidad de medida", bold)
        worksheet.write(row, col + 15, "Código del Método de valuación de existencias aplicado", bold)
        worksheet.write(row, col + 16, "Cantidad de unidades físicas del bien ingresado)", bold)
        worksheet.write(row, col + 17, "Costo unitario del bien ingresado", bold)
        worksheet.write(row, col + 18, "Costo total del bien ingresado", bold)
        worksheet.write(row, col + 19, "Cantidad de unidades físicas del bien retirado", bold)
        worksheet.write(row, col + 20, "Costo unitario del bien retirado", bold)
        worksheet.write(row, col + 21, "Costo total del bien retirado", bold)
        worksheet.write(row, col + 22, "Cantidad de unidades físicas del saldo final", bold)
        worksheet.write(row, col + 23, "Costo unitario del saldo final", bold)
        worksheet.write(row, col + 24, "Costo total del saldo final", bold)
        worksheet.write(row, col + 25, "Indica el estado de la operación", bold)
        worksheet.write(row, col + 26, "Campos de libre utilización", bold)

        # worksheet.set_row(row, 60)
        worksheet.set_column('N:N', 46, None)
        worksheet.set_column('A:A', 9, None)
        worksheet.set_column('I:I', 12, None)

        row += 1

        # Iterador
        for line in lst_move_line:
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

            # Validaciones
            if out_price_unit == 0 and out_quantity == 0:
                out_price_unit = ""
                out_total = ""
            if in_price_unit == 0 and in_quantity == 0:
                in_price_unit = ""
                in_total = ""

            # Asiento Contable
            cuo = ""
            journal = self.env['account.move'].search([('ref', 'like', line.reference)], limit=1)
            if journal:
                cuo = journal.name

            # Código de establecimiento anexo
            codigo_esta = ""
            num_serie = ""
            num_doc = ""
            if line.reference:
                datos = line.reference.split("/")
                if len(datos) > 2:
                    codigo_esta = datos[0]
                    num_serie = datos[1]
                    num_doc = datos[2]

            # Catalogo
            catalogo = ""
            if line.product_id.catalog_id:
                catalogo = line.product_id.catalog_id.number

            # Existencia
            existencia = ""
            if line.product_id.type_existence_id:
                existencia = line.product_id.type_existence_id.number

            # Journal Date
            journal_date = ""
            if line.date:
                journal_date = line.date.strftime("%d/%m/%Y")

            # Tipo de documento
            type_doc = ""
            if line.picking_id.document_type_id:
                type_doc = line.picking_id.document_type_id.number

            # Tipo de operacion
            type_ope = ""
            if line.picking_id.type_operation_id:
                type_ope = line.picking_id.type_operation_id.number

            # Metodo de Evaluación
            met_eva = ""
            if line.product_id.categ_id.property_cost_method == "average":
                met_eva = "01"
            else:
                if line.product_id.categ_id.property_cost_method == "fifo":
                    met_eva = "02"
                else:
                    met_eva = "09"

            # Estado de Operación
            estado_ope = ""
            if line.date.strftime("%m%Y") == time.strftime("%m%Y"):
                estado_ope = "01"
            else:
                if line.date.strftime("%Y") != time.strftime("%Y"):
                    estado_ope = "09"
                else:
                    if int(time.strftime("%m")) == int(line.date.strftime("%m")) - 1:
                        estado_ope = "01"
                    else:
                        estado_ope = "09"

            worksheet.write(row, col, line.date.strftime("%Y%m00") or "")
            worksheet.write(row, col + 1, cuo or "")
            worksheet.write(row, col + 2, journal.id or "")
            worksheet.write(row, col + 3, codigo_esta or "")
            worksheet.write(row, col + 4, catalogo or "")
            worksheet.write(row, col + 5, existencia or "")
            worksheet.write(row, col + 6, line.product_id.default_code or "")
            worksheet.write(row, col + 7, line.product_id.existence_code or "")

            worksheet.write(row, col + 8, journal_date or "")
            worksheet.write(row, col + 9, type_doc or "")

            worksheet.write(row, col + 10, num_serie or "")
            worksheet.write(row, col + 11, num_doc or "")
            worksheet.write(row, col + 12, type_ope or "")

            # Nombre del Producto
            worksheet.write(row, col + 13, line.product_id.display_name or "")
            worksheet.write(row, col + 14, line.product_id.uom_id.sunat_code or "")
            worksheet.write(row, col + 15, met_eva or "")
            # Ingreso
            worksheet.write(row, col + 16, in_quantity or "")
            worksheet.write(row, col + 17, in_price_unit)
            worksheet.write(row, col + 18, in_total)
            # Salidas
            worksheet.write(row, col + 19, out_quantity or "")
            worksheet.write(row, col + 20, out_price_unit)
            worksheet.write(row, col + 21, out_total)
            # Saldo
            worksheet.write(row, col + 22, line.balance_quantity)
            worksheet.write(row, col + 23, line.historical_cost)
            worksheet.write(row, col + 24, total)

            # Demas
            worksheet.write(row, col + 25, estado_ope)

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
