from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import logging

_logger = logging.getLogger(__name__)


class AccountInvoiceConfirm(models.TransientModel):
    # class AccountInvoiceConfirm(models.Model):
    _name = "sunat.purchase_report"
    _description = "Generate TXT"

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    # Parametros
    date_month = fields.Char(string="Mes", size=2)
    date_year = fields.Char(string="Año", size=4)

    @api.multi
    def generate_file(self):
        dominio = [('type', 'like', 'in_invoice'),
                   ('state', 'not like', 'draft'),
                   ('month_year_inv', 'like', self.date_month + "" + self.date_year)
                   # ('month_year_inv', 'like', '032019')
                   ]
        # inv_ids = self._context.get('active_ids')
        # invoice_ids = self.env['account.invoice'].browse(inv_ids)
        invoice_ids = self.env['account.invoice'].search(dominio, order="id asc")

        if len(invoice_ids) == 0:
            raise ValidationError("No se encontraton facturas")

        content = ""

        ruc = False

        for inv in invoice_ids:

            if not ruc or len(ruc) < 7:
                ruc = inv.company_id.vat

            Campo20 = 0
            for line in inv.invoice_line_ids:
                for imp in line.invoice_line_tax_ids:
                    if imp.name.upper() == "otros conceptos".upper():
                        Campo20 = inv.amount_untaxed

            Campo21 = 0
            Campo22 = ''
            Campo23 = ''
            if inv.detrac_id:
                if inv.detrac_id.name.upper() != "no aplica".upper():
                    Campo21 = 1
                    Campo22 = inv.detrac_id.number
                    Campo23 = inv.num_detraction

            Campo24 = 0
            if inv.detrac_id:
                if inv.detrac_id.name.upper() == "no aplica".upper():
                    Campo24 = 1

            Campo29 = 0
            Campo30 = 0
            if inv.type_purchase:
                Campo29 = inv.amount_untaxed
                Campo30 = inv.amount_tax

            txt_line_detalle = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|" \
                               "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|" % (
                                   inv.type_purchase[:2] if inv.type_purchase else '',
                                   inv.document_type_id.number or '',
                                   inv.date_document.strftime("%d/%m/%Y") if inv.date_document else '',
                                   str(inv.document_type_id.number) + str(inv.invoice_number) \
                                       if inv.document_type_id.number and inv.invoice_number else '',
                                   inv.partner_id.person_type[:2] if inv.partner_id.person_type else '',
                                   inv.partner_id.catalog_06_id.code.zfill(2) \
                                       if inv.partner_id.catalog_06_id.code else '',
                                   inv.partner_id.vat or '',
                                   inv.partner_id.name or '',
                                   inv.partner_id.ape_pat or '',
                                   inv.partner_id.ape_mat or '',
                                   inv.partner_id.nombres or '',
                                   '',
                                   inv.currency_id.name,
                                   inv.type_operation,
                                   '1' if inv.type_operation else '',
                                   inv.base_imp or '',
                                   inv.inv_isc or '',
                                   inv.base_igv or '',
                                   Campo20 or '',
                                   Campo21,
                                   Campo22 or '',
                                   Campo23 or '',
                                   Campo24,
                                   inv.refund_invoice_id.document_type_id.number or '',
                                   inv.refund_invoice_id.invoice_serie or '',
                                   inv.refund_invoice_id.invoice_number or '',
                                   inv.refund_invoice_id.date_document.strftime("%d/%m/%Y") \
                                       if inv.refund_invoice_id.date_document else '',
                                   Campo29 or '',
                                   Campo30 or '',
                               )

            # content = content + "" + txt_line_detalle + "<br/>"
            content = content + "" + txt_line_detalle + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content.encode('ISO-8859-1')),
            'txt_filename': "c%s%s%s.txt" % (
                ruc or '00000000000',
                self.date_year,
                self.date_month
            )
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Generar TXT',
            'res_model': 'sunat.purchase_report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
        # return content
