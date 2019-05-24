from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class InventoryValorized(models.TransientModel):
    _name = "sunat.payment_internet"
    _description = "Pago de Detracciones por Internet"

    date_month = fields.Selection(string="Mes", selection=[('01', 'Enero'),
                                                           ('02', 'Febrero'),
                                                           ('03', 'Marzo'),
                                                           ('04', 'Abril'),
                                                           ('05', 'Mayo'),
                                                           ('06', 'Junio'),
                                                           ('07', 'Julio'),
                                                           ('08', 'Agosto'),
                                                           ('09', 'Septiembre'),
                                                           ('10', 'Octubre'),
                                                           ('11', 'Noviembre'),
                                                           ('12', 'Diciembre')])
    date_year = fields.Char(string="Año", size=4)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    # @api.multi
    def generate_file(self):
        date_year = '2019'
        filter_year = 0
        if not date_year.isdigit():
            raise ValidationError("Año Incorrecto")
        else:
            filter_year = int(date_year)

        content_txt = ""
        lst_payments = self.env['account.payment'].search([
            ('type', 'like', 'detraccion'),
            ('month_year_inv', 'like', self.date_month + "" + self.date_year)
        ])

        company = False
        num_lote = ""
        total_monto = 0

        salto_linea = "\r\n"
        # salto_linea = "<br/>"

        for line in lst_payments:

            if not company:
                company = line.company_id
                num_lote = line.name.split("/")[1][2:] + str(line.number_payment).zfill(4)

            for line_pay in line.line_ids:

                num_cuenta = 0
                for banco in line_pay.invoice_id.partner_id.bank_ids:
                    if not num_cuenta and banco.is_detraction:
                        num_cuenta = banco.acc_number if banco.acc_number else 0

                txt_line_detalle = "%s%s%s%s%s%s%s%s%s%s%s%s" % (
                    '6',  # 1 ->
                    line.partner_id.vat,  # 2 ->
                    line.partner_id.name.ljust(35, ' ') or "",  # 3 ->
                    '000000000',  # 4 ->
                    str(line_pay.invoice_id.code_goods_id.number).zfill(3) \
                        if line_pay.invoice_id.code_goods_id else "0".zfill(3),  # 5 ->
                    str(num_cuenta).zfill(11) or '',  # 6 ->
                    str("{:.2f}".format(line.amount).replace('.', '')).zfill(15) or "0".zfill(15),  # 7 ->
                    line_pay.invoice_id.type_operation_id.number or '',  # 8 ->
                    line_pay.invoice_id.date_invoice.strftime("%Y%m") if line_pay.invoice_id.date_invoice else "",  # 9
                    line_pay.invoice_id.document_type_id.number or '',  # 10 ->
                    line_pay.invoice_id.invoice_serie.zfill(4) or '',  # 11 ->
                    line_pay.invoice_id.invoice_number.zfill(8) or '',  # 12 ->
                )

                total_monto = total_monto + line.amount

                # Agregamos la linea al TXT
                content_txt = content_txt + "" + txt_line_detalle + salto_linea

        if len(lst_payments) > 0:
            txt_line_cabezera = "%s%s%s%s%s" % (
                '*',  # 1 ->
                '20547582510',  # 2 ->
                company.name.ljust(35, ' ') if company else "",  # 3 ->
                num_lote or "",  # 4 ->
                str("{:.2f}".format(total_monto).replace('.', '')).zfill(15) or "0".zfill(15),  # 5 ->
            )

            content_txt = txt_line_cabezera + salto_linea + content_txt

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "D10000000065%s.txt" % (num_lote)
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Pago de Detracciones por Internet',
            'res_model': 'sunat.payment_internet',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
        # return content_txt
