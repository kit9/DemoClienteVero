from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from io import BytesIO
import xlsxwriter
import base64
import logging
import time

_logger = logging.getLogger(__name__)


def cel(row, colum):
    return str(colum) + str(row)


def merge(row, colum, row2, colum2):
    return cel(row, colum) + ':' + cel(row2, colum2)


center = {'align': 'center', 'valign': 'vcenter'}
vcenter = {'valign': 'vcenter'}
border = {'border': 1}
bold = {'bold': 1}
border2 = {'border': 2}
b_right_x = {'right': 0}
b_left_x = {'left': 0}
b_top_only = {'left': 0, 'right': 0, 'bottom': 0}
right = {'align': 'right'}
left = {'align': 'left'}
text_wrap = {'text_wrap': 1}


def merge_dicts(workbook, *dict_args):
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return workbook.add_format(result)


class DrowbackDrowback(models.TransientModel):
    _name = "drowback.drowback"
    _description = "Drowback"

    # @api.model
    # def default_get(self, fields):
    #     pik_ids = self._context.get('active_ids')
    #     picking_ids = self.env['stock.picking'].browse(pik_ids)
    #     for picking in picking_ids:
    #
    #     return {}

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    # invoice_ids = fields.One2many('bulk.invoice', 'bulk_invoice_id', string='Invoice')

    @api.multi
    def generate_file(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        pik_ids = self._context.get('active_ids')
        picking_ids = self.env['stock.picking'].browse(pik_ids)

        # Create a format to use in the merged range.
        merge_format = workbook.add_format({
            'border': 1,
        })
        # 'fg_color': 'yellow'

        worksheet.set_column('B:B', 22, None)
        worksheet.set_column('C:C', 7, None)
        worksheet.set_column('D:D', 12, None)
        worksheet.set_column('F:F', 11, None)
        worksheet.set_column('J:J', 13, None)
        worksheet.set_column('H:H', 18, None)
        worksheet.set_column('I:I', 11, None)
        worksheet.set_column('M:M', 12, None)
        worksheet.set_column('K:L', 10, None)
        worksheet.set_row(10, 30)  # Set the height of Row 1 to 20.

        row = 2

        title_format = {
            'bold': 1,
            'font_name': 'Times New Roman'
        }

        product_export = []
        for picking in picking_ids:

            # Validaciones
            if not picking.dua_code:
                raise ValidationError("Se debe de llenar el Codigo de Dua en " + str(picking.name))
            if not picking.dua_year:
                raise ValidationError("Se debe de llenar el Año de Dua en " + str(picking.name))
            if not picking.boarding_date:
                raise ValidationError("Se debe de llenar la Fecha de Embarque en " + str(picking.name))
            if not picking.dua_serie:
                raise ValidationError("Se debe de llenar la Serie de Dua en " + str(picking.name))
            if not picking.dua_number:
                raise ValidationError("Se debe de llenar el Número de Dua en " + str(picking.name))
            if not picking.invoice_id:
                raise ValidationError("Se debe de llenar la Factura en " + str(picking.name))

            input = False
            ingredient = False

            for picking_line in picking.move_ids_without_package:
                product_valid = False
                for bom_line in picking_line.product_id.bom_ids:
                    for line_line in bom_line.bom_line_ids:
                        if line_line.product_id and line_line.product_id.is_imported_product:
                            product_valid = True
                            if not input:
                                input = line_line.product_id
                            if not ingredient:
                                ingredient = line_line
                if product_valid:
                    product_export.append(picking_line.product_id)

            for product in product_export:
                _logger.info(product.name)

                input_invoice_line = False
                if input:
                    domain = [('invoice_id.document_type_id.number', '=', '50'),
                              ('product_id', '=', input.id),
                              ('invoice_id.state', 'in', ['open', 'paid'])]
                    input_invoice_line = self.env['account.invoice.line'].search(domain, limit=1)

                # Titulo
                worksheet.merge_range(merge(row, 'B', row, 'M'),  # 'B2:M2',
                                      'SOLICITUD DE RESTITUCION SECCION II - RELACION DE INSUMOS IMPORTADOS',
                                      merge_dicts(workbook, center, title_format, bold))

                row = row + 3

                # Campo
                worksheet.merge_range(merge(row, 'B', row, 'E'),  # 'B5:E5',
                                      'DECLARACION UNICA O SIMPLIFICADA DE EXPORTACION',
                                      merge_dicts(workbook, center, bold, border))

                row = row + 1

                DAM = ""
                if picking.dua_code:
                    DAM = str(picking.dua_code.number)
                if picking.dua_year:
                    DAM = DAM + "-" + picking.dua_year
                DAM = DAM + "-41"
                if picking.dua_number:
                    DAM = DAM + picking.dua_number

                # Valores
                worksheet.merge_range('B6:E6',
                                      'N° ' + str(DAM),
                                      merge_format)

                row = row + 1  # 7

                # Campo
                worksheet.write(cel(row, 'B'), '1.SERIE',
                                merge_dicts(workbook, border, bold))
                worksheet.merge_range(merge(row, 'C', row, 'I'),
                                      '1.1 DESCRIPCION DE LA MERCANCIA EXPORTADA',
                                      merge_dicts(workbook, border, bold))
                worksheet.merge_range(merge(row, 'J', row, 'M'), '1.2 FOB SUJETO A RESTITUCIÓN',
                                      merge_dicts(workbook, border, bold))

                # Valores
                worksheet.write(cel(row + 1, 'B'), '1', merge_format)
                worksheet.merge_range(merge(row + 1, 'C', row + 1, 'I'),
                                      product.display_name if product.display_name else "",
                                      merge_format)
                # Moneda
                worksheet.merge_range(merge(row + 1, 'J', row + 1, 'K'),  # cel(row + 1, 'J'),
                                      picking.invoice_id.currency_id.symbol
                                      if picking.invoice_id.currency_id.symbol else "",
                                      merge_dicts(workbook, right, border))
                worksheet.merge_range(merge(row + 1, 'L', row + 1, 'M'),  # cel(row + 1, 'K'),
                                      str(picking.sale_id.amount_total)
                                      if picking.sale_id.amount_total else "",
                                      merge_dicts(workbook, left, border))

                # # Campo
                worksheet.merge_range(merge(row + 2, 'B', row + 2, 'I'),  # 'B9:I9',
                                      '2. DETALLE DE LA MERCANCIA IMPORTADA POR SERIE DE EXPORTACION',
                                      merge_dicts(workbook, border, bold))
                worksheet.merge_range(merge(row + 2, 'J', row + 2, 'M'),  # 'J9:M9',
                                      '3. CANTIDAD DE INSUMO',
                                      merge_dicts(workbook, border, bold))

                # Campo
                worksheet.merge_range(merge(row + 3, 'B', row + 3, 'C'),  # 'B10:C10',
                                      '2.1 DECLARACION',
                                      merge_dicts(workbook, border, bold))
                worksheet.merge_range(merge(row + 3, 'D', row + 3, 'F'),  # 'D10:F10',
                                      '2.2 FACTURA COMPRA LOCAL',
                                      merge_dicts(workbook, border, bold))
                worksheet.merge_range(merge(row + 3, 'G', row + 4, 'H'),  # 'G10:H11',
                                      '2.3 DESCRIPCION DE LA MERCANCIA',
                                      merge_dicts(workbook, border, text_wrap, center, bold))
                worksheet.merge_range(merge(row + 3, 'I', row + 4, 'I'),  # 'I10:I11',
                                      '2.4 UNIDAD DE MEDIDA',
                                      merge_dicts(workbook, border, text_wrap, center, bold))
                worksheet.merge_range(merge(row + 3, 'J', row + 4, 'J'),  # 'J10:J11',
                                      '3.1 CONTENIDO NETO',
                                      merge_dicts(workbook, border, text_wrap, center, bold))
                worksheet.merge_range(merge(row + 3, 'K', row + 3, 'L'),  # 'K10:L10',
                                      '3.2 EXCEDENTES CON / SIN VALOR COMERCIAL',
                                      merge_dicts(workbook, border, text_wrap, center, bold))
                worksheet.write(cel(row + 4, 'K'),  # 'K11',
                                'C / V',
                                merge_dicts(workbook, border, bold, center))
                worksheet.write(cel(row + 4, 'L'),  # 'L11',
                                'S / V',
                                merge_dicts(workbook, border, bold, center))
                worksheet.write(cel(row + 3, 'M'),  # 'M10',
                                '3.3 INSUMO UTILIZADO',
                                merge_dicts(workbook, border, text_wrap, center, bold))
                worksheet.write(cel(row + 4, 'M'),  # 'M11',
                                '3.1 + 3.2',
                                merge_dicts(workbook, border, bold, center))

                # Campo
                worksheet.write(cel(row + 4, 'B'),  # 'B11',
                                'AD-ANO-COD-NUMERO',
                                merge_dicts(workbook, border, bold, center))
                worksheet.write(cel(row + 4, 'C'),  # 'C11',
                                'SERIE',
                                merge_dicts(workbook, border, bold, center))
                worksheet.write(cel(row + 4, 'D'),  # 'D11',
                                'RUC PROVEEDOR',
                                merge_dicts(workbook, border, text_wrap, center, bold))
                worksheet.write(cel(row + 4, 'E'),  # 'E11',
                                'NUMERO',
                                merge_dicts(workbook, border, bold, center))
                worksheet.write(cel(row + 4, 'F'),  # 'G11',
                                'FECHA',
                                merge_dicts(workbook, border, bold, center))

                worksheet.set_row((row + 3) - 1, 30)
                worksheet.set_row((row + 4) - 1, 30)

                # AD-ANO-COD-NUMERO
                AD_ANO_COD_NUMERO = ""
                if input_invoice_line.invoice_id.code_dua:
                    AD_ANO_COD_NUMERO = str(input_invoice_line.invoice_id.code_dua.number)
                if input_invoice_line.invoice_id.year_emission_dua:
                    AD_ANO_COD_NUMERO = AD_ANO_COD_NUMERO + "-" + input_invoice_line.invoice_id.year_emission_dua
                AD_ANO_COD_NUMERO = AD_ANO_COD_NUMERO + "-41"
                if input_invoice_line.invoice_id.invoice_number:
                    AD_ANO_COD_NUMERO = AD_ANO_COD_NUMERO + "-" + input_invoice_line.invoice_id.invoice_number

                row = row + 4
                row = row + 1
                _logger.info("Llenando datos")
                worksheet.write(cel(row, 'B'),
                                AD_ANO_COD_NUMERO if
                                input_invoice_line else "",
                                merge_format)
                # Serie
                worksheet.merge_range(merge(row, 'C', row + 1, 'C'),
                                      '1/1',
                                      merge_format)
                # RUC
                worksheet.merge_range(merge(row, 'D', row + 1, 'D'),
                                      str(input_invoice_line.invoice_id.partner_id.vat or ""),
                                      merge_format)
                # NUMERO
                worksheet.merge_range(merge(row, 'E', row + 1, 'E'),
                                      input_invoice_line.invoice_id.invoice_number if
                                      input_invoice_line.invoice_id.invoice_number else "",
                                      merge_format)
                # FECHA
                worksheet.merge_range(merge(row, 'F', row + 1, 'F'),
                                      input_invoice_line.invoice_id.date_document.strftime("%d/%m/%Y")
                                      if input_invoice_line.invoice_id.date_document else "",
                                      merge_format)
                # Producto
                worksheet.merge_range(merge(row, 'G', row + 1, 'H'),
                                      input.display_name
                                      if input.display_name else "",
                                      merge_format)
                # Unidad de Medida
                worksheet.merge_range(merge(row, 'I', row + 1, 'I'),
                                      input.uom_id.name
                                      if input.uom_id.name else "",
                                      merge_format)

                worksheet.merge_range(merge(row, 'J', row + 1, 'J'), '', merge_format)
                worksheet.merge_range(merge(row, 'K', row + 1, 'K'), '', merge_format)
                worksheet.merge_range(merge(row, 'L', row + 1, 'L'), '', merge_format)
                worksheet.merge_range(merge(row, 'M', row + 1, 'M'),
                                      str(ingredient.product_qty)
                                      if ingredient.product_qty else "",
                                      merge_format)
                row = row + 1
                worksheet.write(cel(row, 'B'),
                                'RUC',
                                merge_dicts(workbook, border, bold))

                for line_line in range(2):
                    row = row + 1
                    worksheet.write(cel(row, 'B'), '', merge_format)
                    worksheet.merge_range(merge(row, 'C', row + 1, 'C'), '', merge_format)
                    worksheet.merge_range(merge(row, 'D', row + 1, 'D'), '', merge_format)
                    worksheet.merge_range(merge(row, 'E', row + 1, 'E'), '', merge_format)
                    worksheet.merge_range(merge(row, 'F', row + 1, 'F'), '', merge_format)
                    worksheet.merge_range(merge(row, 'G', row + 1, 'H'), '', merge_format)
                    worksheet.merge_range(merge(row, 'I', row + 1, 'I'), '', merge_format)
                    worksheet.merge_range(merge(row, 'J', row + 1, 'J'), '', merge_format)
                    worksheet.merge_range(merge(row, 'K', row + 1, 'K'), '', merge_format)
                    worksheet.merge_range(merge(row, 'L', row + 1, 'L'), '', merge_format)
                    worksheet.merge_range(merge(row, 'M', row + 1, 'M'), '', merge_format)
                    row = row + 1
                    worksheet.write(cel(row, 'B'), 'RUC', merge_format)

                # --------------------------------------------------------------------------------------------------------------

                # row = row + 1  # 7
                # # Campo
                # worksheet.write(cel(row, 'B'), '1.SERIE', merge_format)
                # worksheet.merge_range(merge(row, 'C', row, 'I'),
                #                       '1.1 DESCRIPCION DE LA MERCANCIA EXPORTADA',
                #                       merge_format)
                # worksheet.merge_range(merge(row, 'J', row, 'M'), '1.2 FOB SUJETO A RESTITUCIÓN', merge_format)
                #
                # # Valores
                # worksheet.write(cel(row + 1, 'B'), '1', merge_format)
                # worksheet.merge_range(merge(row + 1, 'C', row + 1, 'I'), '1.1 ESPARRAGOS FRESCOS', merge_format)
                # worksheet.merge_range(merge(row + 1, 'J', row + 1, 'K'),  # cel(row + 1, 'J'),
                #                       'US$',
                #                       merge_dicts(workbook, right, border))
                # worksheet.merge_range(merge(row + 1, 'L', row + 1, 'M'),  # cel(row + 1, 'K'),
                #                       '499977.51',
                #                       merge_dicts(workbook, left, border))
                #
                # # # Campo
                # worksheet.merge_range(merge(row + 2, 'B', row + 2, 'I'),  # 'B9:I9',
                #                       '2. DETALLE DE LA MERCANCIA IMPORTADA POR SERIE DE EXPORTACION',
                #                       merge_format)
                # worksheet.merge_range(merge(row + 2, 'J', row + 2, 'M'),  # 'J9:M9',
                #                       '3. CANTIDAD DE INSUMO', merge_format)
                #
                # # Campo
                # worksheet.merge_range(merge(row + 3, 'B', row + 3, 'C'),  # 'B10:C10',
                #                       '2.1 DECLARACION', merge_format)
                # worksheet.merge_range(merge(row + 3, 'D', row + 3, 'F'),  # 'D10:F10',
                #                       '2.2 FACTURA COMPRA LOCAL', merge_format)
                # worksheet.merge_range(merge(row + 3, 'G', row + 4, 'H'),  # 'G10:H11',
                #                       '2.3 DESCRIPCION DE LA MERCANCIA',
                #                       merge_dicts(workbook, border, text_wrap, center))
                # worksheet.merge_range(merge(row + 3, 'I', row + 4, 'I'),  # 'I10:I11',
                #                       '2.4 UNIDAD DE MEDIDA',
                #                       merge_dicts(workbook, border, text_wrap, center))
                # worksheet.merge_range(merge(row + 3, 'J', row + 4, 'J'),  # 'J10:J11',
                #                       '3.1 CONTENIDO NETO',
                #                       merge_dicts(workbook, border, text_wrap, center))
                # worksheet.merge_range(merge(row + 3, 'K', row + 3, 'L'),  # 'K10:L10',
                #                       '3.2 EXCEDENTES CON / SIN VALOR COMERCIAL',
                #                       merge_dicts(workbook, border, text_wrap, center))
                # worksheet.write(cel(row + 4, 'K'),  # 'K11',
                #                 'C / V', merge_format)
                # worksheet.write(cel(row + 4, 'L'),  # 'L11',
                #                 'S / V', merge_format)
                # worksheet.write(cel(row + 3, 'M'),  # 'M10',
                #                 '3.3 INSUMO UTILIZADO',
                #                 merge_dicts(workbook, border, text_wrap, center))
                # worksheet.write(cel(row + 4, 'M'),  # 'M11',
                #                 '3.1 + 3.2', merge_format)
                #
                # # Campo
                # worksheet.write(cel(row + 4, 'B'),  # 'B11',
                #                 'AD-ANO-COD-NUMERO', merge_format)
                # worksheet.write(cel(row + 4, 'C'),  # 'C11',
                #                 'SERIE', merge_format)
                # worksheet.write(cel(row + 4, 'D'),  # 'D11',
                #                 'RUC PROVEEDOR',
                #                 merge_dicts(workbook, border, text_wrap, center))
                # worksheet.write(cel(row + 4, 'E'),  # 'E11',
                #                 'NUMERO', merge_format)
                # worksheet.write(cel(row + 4, 'F'),  # 'G11',
                #                 'FECHA', merge_format)
                #
                # worksheet.set_row((row + 3) - 1, 30)
                # worksheet.set_row((row + 4) - 1, 30)
                #
                # row = row + 4
                # for line_line in range(3):
                #     row = row + 1
                #     worksheet.write(cel(row, 'B'), '', merge_format)
                #     worksheet.merge_range(merge(row, 'C', row + 1, 'C'), '', merge_format)
                #     worksheet.merge_range(merge(row, 'D', row + 1, 'D'), '', merge_format)
                #     worksheet.merge_range(merge(row, 'E', row + 1, 'E'), '', merge_format)
                #     worksheet.merge_range(merge(row, 'F', row + 1, 'F'), '', merge_format)
                #     worksheet.merge_range(merge(row, 'G', row + 1, 'H'), '', merge_format)
                #     worksheet.merge_range(merge(row, 'I', row + 1, 'I'), '', merge_format)
                #     worksheet.merge_range(merge(row, 'J', row + 1, 'J'), '', merge_format)
                #     worksheet.merge_range(merge(row, 'K', row + 1, 'K'), '', merge_format)
                #     worksheet.merge_range(merge(row, 'L', row + 1, 'L'), '', merge_format)
                #     worksheet.merge_range(merge(row, 'M', row + 1, 'M'), '', merge_format)
                #     row = row + 1
                #     worksheet.write(cel(row, 'B'), 'RUC', merge_format)

                # --------------------------------------------------------------------------------------------------------------

                row = row + 1

                worksheet.merge_range(merge(row, 'I', row + 1, 'J'),
                                      '4. TOTAL FOB RESTITUCION POR DECLARACION',
                                      merge_dicts(workbook, center, text_wrap))
                # Moneda
                worksheet.merge_range(merge(row, 'K', row + 1, 'K'),
                                      picking.invoice_id.currency_id.symbol
                                      if picking.invoice_id.currency_id.symbol else "",
                                      merge_dicts(workbook, border, b_right_x, right, vcenter))
                # Total
                worksheet.merge_range(merge(row, 'L', row + 1, 'M'),
                                      str(picking.sale_id.amount_total)
                                      if picking.sale_id.amount_total else "",
                                      merge_dicts(workbook, border, b_left_x, left, vcenter))

                row = row + 1

                worksheet.merge_range(merge(row, 'B', row, 'G'),
                                      'EL PRESENTE DOCUMENTO TIENEN CARACTER DE DECLARACION JURADA',
                                      merge_dicts(workbook, center))

                row = row + 3

                worksheet.merge_range(merge(row, 'G', row, 'J'),
                                      self.env.user.company_id.legal_representative.name if
                                      self.env.user.company_id.legal_representative.name else "",
                                      merge_dicts(workbook, center, border2, b_top_only))

                row = row + 1

                worksheet.merge_range(merge(row, 'G', row, 'J'),
                                      'REPRESENTANTE LEGAL DE LA EMPRESA',
                                      merge_dicts(workbook, center))

        # --------------------------------------------------------------------------------------------------------------
        # worksheet.set_default_row(hide_unused_rows=True)
        # for row in range(1, 7):
        #     worksheet.set_row(row, 15)
        worksheet.set_row(0, 0)
        # worksheet.set_row(2, 15)
        # worksheet.set_row(3, 15)
        worksheet.set_column('A:A', None, None, {'hidden': True})

        workbook.close()
        output.seek(0)

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(output.getvalue()),
            'txt_filename': "drowback.xlsx"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Drowback',
            'res_model': 'drowback.drowback',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
