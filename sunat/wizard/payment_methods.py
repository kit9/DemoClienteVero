from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import logging

_logger = logging.getLogger(__name__)


class AccountInvoiceConfirm(models.TransientModel):
    # class AccountInvoiceConfirm(models.Model):
    _name = "sunat.payment_methods_report"
    _description = "Generate TXT"

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    # Parametros
    date_month = fields.Char(string="Mes", size=2)
    date_year = fields.Char(string="Año", size=4)

    @api.multi
    def generate_file(self):
        dominio = [  # ('type', 'like', 'in_invoice'),
            ('state', 'like', 'posted'),
            # ('month_year_inv', 'like', self.date_month + "" + self.date_year)
            ('month_year_inv', 'like', '032019')
        ]
        # inv_ids = self._context.get('active_ids')
        # invoice_ids = self.env['account.invoice'].browse(inv_ids)
        payment_ids = self.env['account.payment'].search(dominio, order="id asc")

        if len(payment_ids) == 0:
            raise ValidationError("No se encontraton facturas")

        content = ""

        ruc = False

        for payment in payment_ids:

            for line in payment.line_ids:

                if not ruc or len(ruc) < 7:
                    ruc = line.invoice_id.company_id.vat

                txt_line_detalle = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                    line.invoice_id.type_purchase[:2] if line.invoice_id.type_purchase else '',
                    line.invoice_id.document_type_id.number or '',
                    line.invoice_id.invoice_serie or '',
                    line.invoice_id.invoice_number or '',
                    line.invoice_id.partner_id.person_type[:2] if line.invoice_id.partner_id.person_type else '',
                    line.invoice_id.partner_id.catalog_06_id.code.zfill(2) \
                        if line.invoice_id.partner_id.catalog_06_id.code else '',
                    line.invoice_id.partner_id.vat or '',
                    payment.payment_methods_id.number if payment.payment_methods_id else '',
                    payment.operation_number or '',
                    payment.payment_date.strftime("%d/%m/%Y") if payment.payment_date else '',
                    line.allocation or '',
                )

                # content = content + "" + txt_line_detalle + "<br/>"
                content = content + "" + txt_line_detalle + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content.encode('ISO-8859-1')),
            'txt_filename': "F%s%s%s.txt" % (
                ruc or '00000000000',
                self.date_year,
                self.date_month
            )
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Generar TXT',
            'res_model': 'sunat.payment_methods_report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
        # return content
