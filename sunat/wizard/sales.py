from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import logging

_logger = logging.getLogger(__name__)


class AccountInvoiceConfirm(models.TransientModel):
    # class AccountInvoiceConfirm(models.Model):
    _name = "sunat.sales_report"
    _description = "Generate TXT"

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    # Parametros
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

    @api.multi
    def generate_file(self):
        dominio = [('type', 'in', ['out_invoice', 'out_refund']),
                   ('state', 'not like', 'draft'),
                   ('month_year_inv', 'like', self.date_month + "" + self.date_year)
                   # ('month_year_inv', 'like', '032019')
                   ]
        invoice_ids = self.env['account.invoice'].search(dominio, order="id asc")

        if len(invoice_ids) == 0:
            raise ValidationError("No se encontraton facturas")

        content = ""

        ruc = False

        for inv in invoice_ids:

            if not ruc or len(ruc) < 7:
                ruc = inv.company_id.vat

            campo14 = 9
            if inv.currency_id.name == "PEN":
                campo14 = 1
            elif inv.currency_id.name == "USD":
                campo14 = 2

            campo16 = 0
            if inv.inv_type_operation == '1' or inv.inv_type_operation == '2':
                campo16 = 1
            elif inv.inv_type_operation == '3':
                campo16 = 2

            if len(inv.payment_ids) > 0:
                for payment in inv.payment_ids:
                    txt_line_detalle = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|" \
                                       "%s|%s|%s|%s|%s|%s|%s|%s|" % (
                                           inv.type_sales[:2] if inv.type_sales else '',
                                           inv.document_type_id.number or '',
                                           payment.payment_date.strftime("%d/%m/%Y") \
                                               if payment.payment_date else '',
                                           inv.invoice_serie or '',
                                           inv.invoice_number or '',
                                           inv.partner_id.person_type[:2] if inv.partner_id.person_type else '',
                                           inv.partner_id.catalog_06_id.code.zfill(2) \
                                               if inv.partner_id.catalog_06_id.code else '',
                                           inv.partner_id.vat or '',
                                           inv.partner_id.name or '',
                                           inv.partner_id.ape_pat or '',
                                           inv.partner_id.ape_mat or '',
                                           inv.partner_id.nombres or '',
                                           '',
                                           campo14 or '',
                                           inv.inv_type_operation or '',
                                           campo16 or '',
                                           inv.inv_amount_untax or '',
                                           inv.inv_isc or '',
                                           inv.amount_tax or '',
                                           inv.inv_otros or '',
                                           '1' if inv.perception_id else '0',  # 21 ->
                                           inv.perception_id.number.zfill(2) if inv.perception_id else '',  # 22 ->
                                           inv.num_comp_serie or '',
                                           inv.num_perception or '',
                                           inv.refund_invoice_id.document_type_id.number or '',
                                           inv.refund_invoice_id.invoice_serie or '',
                                           inv.refund_invoice_id.invoice_number or '',
                                           inv.refund_invoice_id.date_document.strftime("%d/%m/%Y") \
                                               if inv.refund_invoice_id.date_document else '',
                                           inv.refund_invoice_id.amount_untaxed or '',
                                           inv.refund_invoice_id.amount_tax or '',
                                       )

                    # content = content + "" + txt_line_detalle + "<br/>"
                    content = content + "" + txt_line_detalle + "\r\n"
            else:
                txt_line_detalle = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|" \
                                   "%s|%s|%s|%s|%s|%s|%s|%s|" % (
                                       inv.type_sales[:2] if inv.type_sales else '',
                                       inv.document_type_id.number or '',
                                       '',
                                       inv.invoice_serie or '',
                                       inv.invoice_number or '',
                                       inv.partner_id.person_type[:2] if inv.partner_id.person_type else '',
                                       inv.partner_id.catalog_06_id.code.zfill(2) \
                                           if inv.partner_id.catalog_06_id.code else '',
                                       inv.partner_id.vat or '',
                                       inv.partner_id.name or '',
                                       inv.partner_id.ape_pat or '',
                                       inv.partner_id.ape_mat or '',
                                       inv.partner_id.nombres or '',
                                       '',
                                       campo14 or '',
                                       inv.inv_type_operation or '',
                                       campo16 or '',
                                       inv.inv_amount_untax or '',
                                       inv.inv_isc or '',
                                       inv.amount_tax or '',
                                       inv.inv_otros or '',
                                       '1' if inv.perception_id else '0',  # 21 ->
                                       inv.perception_id.number.zfill(2) if inv.perception_id else '',  # 22 ->
                                       inv.num_comp_serie or '',
                                       inv.num_perception or '',
                                       inv.refund_invoice_id.document_type_id.number or '',
                                       inv.refund_invoice_id.invoice_serie or '',
                                       inv.refund_invoice_id.invoice_number or '',
                                       inv.refund_invoice_id.date_document.strftime("%d/%m/%Y") \
                                           if inv.refund_invoice_id.date_document else '',
                                       inv.refund_invoice_id.amount_untaxed or '',
                                       inv.refund_invoice_id.amount_tax or '',
                                   )

                # content = content + "" + txt_line_detalle + "<br/>"
                content = content + "" + txt_line_detalle + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content.encode('ISO-8859-1')),
            'txt_filename': "V%s%s%s.txt" % (
                ruc or '00000000000',
                self.date_year,
                self.date_month
            )
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Generar TXT',
            'res_model': 'sunat.sales_report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
        # return content
