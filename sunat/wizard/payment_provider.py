from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class InventoryValorized(models.TransientModel):
    # class InventoryValorized(models.Model):
    _name = "sunat.payment_provider"
    _description = "Pago de Proveedores"

    date_month = fields.Char(string="Mes", size=2)
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
            ('type', 'like', 'factura'),
            ('month_year_inv', 'like', self.date_month + "" + self.date_year)
            # ('month_year_inv', 'like', '032019')
        ])

        company = False
        total_monto = 0

        bank_account = self.env['account.journal'].search([], limit=1)

        salto_linea = "\r\n"
        # salto_linea = "<br/>"

        for line in lst_payments:

            if not company:
                company = line.company_id

            for line_pay in line.line_ids:

                num_cuenta = 0
                for banco in line_pay.invoice_id.partner_id.bank_ids:
                    if not num_cuenta and not banco.is_detraction and not banco.is_retention:
                        num_cuenta = banco.acc_number if banco.acc_number else 0

                campo5 = ''
                if line.currency_id.name == "PEN":
                    campo5 = '0001'
                elif line.currency_id.name == "USD":
                    campo5 = '1001'

                txt_line = "%s%s%s%s%s%s%s%s%s%s" % (
                    '1',  # 1 ->
                    # line.partner_id.name or '',  # 2 ->
                    str(len(lst_payments)).zfill(6),  # 2 ->
                    line.payment_date.strftime("%Y%m%d") if line.payment_date else '0'.zfill(8),  # 3 ->
                    bank_account.bank_account_id.account_type or ' ',  # 4 ->
                    campo5.zfill(4),  # 5 ->
                    bank_account.bank_account_id.branch_office.zfill(20) \
                        if bank_account.bank_account_id.branch_office else '0'.zfill(20),  # 6 ->
                    str(line_pay.allocation).zfill(17) if line_pay.allocation else '0'.zfill(17),  # 7 ->
                    line.communication.ljust(40, ' ') \
                        if line.communication else ' '.ljust(40, ' '),  # 8 ->
                    'N',  # 9 ->
                    num_cuenta.zfill(15),  # 10 ->
                )

                total_monto = total_monto + line.amount

                # Agregamos la linea al TXT
                content_txt = content_txt + "" + txt_line + salto_linea

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Pago_Proveedores.txt"
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Pago de Detracciones por Internet',
            'res_model': 'sunat.payment_provider',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
        # return content_txt
