from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class InventoryValorized(models.TransientModel):
    _name = "sunat.inventory_valorized"
    _description = "Estructura del Registro de Inventario Permanente Valorizado"

    date_month = fields.Char(string="Mes", size=2)
    date_year = fields.Char(string="Año", size=4)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        dominio = [('state', 'like', 'done'),
                   ('month_year_inv', 'like', self.date_month + "" + self.date_year)]

        # Data
        lst_move_line = self.env['stock.move.line'].search(dominio, order="product_id,id")

        content_txt = ""

        # Iterador
        for line in lst_move_line:

            # for move in line.move_id.account_move_ids:
            # Cantidad
            in_quantity = 0
            out_quantity = 0.00
            if "OUT" in line.reference:
                out_quantity = line.qty_done
            else:
                in_quantity = line.qty_done

            # Precio Unitario
            in_price_unit = 0.00
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
            if line.move_id.warehouse_id:
                codigo_esta = line.move_id.warehouse_id.code

            # Numeros
            num_serie = ""
            num_doc = ""
            if line.reference:
                datos = line.reference.split("/")
                if len(datos) > 2:
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
            if line.product_id.categ_id:
                met_eva = line.product_id.categ_id.name

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

            if journal:
                txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%.2f|%s|%.2f|%s|%s|%s|%s|%s|%s|" % (
                    line.date.strftime("%Y%m00") or "",  # 1 -> Periodo
                    cuo or "",  # 2 ->
                    # len(line.move_id.account_move_ids),  # 3 ->
                    ("M" + str(journal.id)) if journal.id else '',  # 3 ->
                    codigo_esta or "",  # 4 -> Nombre corto de almacen
                    catalogo or "",  # 5 ->
                    existencia or "",  # 6 ->
                    line.product_id.default_code or "",  # 7 ->
                    line.product_id.existence_code or "",  # 8 ->
                    journal_date or "",  # 9 ->
                    type_doc or "",  # 10 ->
                    num_serie or "",  # 11 ->
                    num_doc or "",  # 12 ->
                    type_ope or "",  # 13 ->
                    line.product_id.display_name or "",  # 14 ->
                    line.product_id.uom_id.sunat_code or "",  # 15 ->
                    met_eva or "",  # 16 ->
                    in_quantity or "",  # 17 ->
                    in_price_unit if in_price_unit else 0.00,  # 18->
                    in_total,  # 19 ->
                    out_quantity if out_quantity else 0.00,  # 20 ->
                    out_price_unit,  # 21 ->
                    out_total,  # 22 ->
                    line.balance_quantity,  # 23 ->
                    line.historical_cost,  # 24 ->
                    total,  # 25 ->
                    estado_ope  # 26 ->
                )

                # Agregamos la linea al TXT
                content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "LE2060158712320190200130100001111.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Estructura del Registro de Inventario Permanente Valorizado',
            'res_model': 'sunat.inventory_valorized',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
