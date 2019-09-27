from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import base64
import logging

_logger = logging.getLogger(__name__)


class AccountInvoiceConfirm(models.TransientModel):
    _name = "account.bill.txt"
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
                                                           ('12', 'Diciembre')],
                                  default=lambda self: datetime.now().date().strftime("%m"))
    date_year = fields.Char(string="Año", size=4, default=lambda self: datetime.now().date().strftime("%Y"))
    type = fields.Selection(string="Factura de", selection=[('out_invoice', 'Clientes'), ('in_invoice', 'Proveedores')])
    company_id = fields.Many2one('res.company', string='Compañia',
                                 default=lambda self: self._context.get('company_id', self.env.user.company_id.id))

    @api.multi
    def generate_file(self):

        if self.type == "out_invoice":
            type_doc = ['out_invoice', 'out_refund']
        elif self.type == "in_invoice":
            type_doc = ['in_invoice']
        else:
            raise ValidationError("No se encontraton facturas")

        dominio = [('type', 'in', type_doc),
                   ('state', 'not like', 'draft'),
                   ('month_year_inv', 'like', self.date_month + "" + self.date_year),
                   ('company_id', '=', self.company_id.id)]

        invoice_ids = self.env['account.invoice'].search(dominio, order="id asc")

        if len(invoice_ids) == 0:
            raise ValidationError("No se encontraton facturas")

        content = ""
        if self.type == "in_invoice":
            for inv in invoice_ids:
                # Obtener el correlativo General de la Factura en el Mes
                correlativo = ""
                dominio = [('month_year_inv', 'like', inv.date_invoice.strftime("%m%Y"))]
                facturas = self.env['account.invoice'].search(dominio, order="id asc")
                contador = 0
                for inv in facturas:
                    contador = contador + 1
                    if inv.number == inv.number:
                        correlativo = "%s" % (contador)

                # Obtener el impuesto otros
                impuesto_otros = ""
                for imp in inv.tax_line_ids:
                    if str(imp.tax_id.tax_rate) == "otros":
                        impuesto_otros = imp.amount_total

                # 26 -> Fecha
                campo_26 = ""
                if inv.refund_invoice_id.date_document:
                    campo_26 = inv.refund_invoice_id.date_document.strftime("%d/%m/%Y")

                # 14 Base imponible
                campo_14 = ""
                if inv.type_operation == "1":
                    campo_14 = inv.amount_untaxed

                # 15 Impuesto
                campo_15 = ""
                if inv.type_operation == "1":
                    for imp in inv.tax_line_ids:
                        if str(imp.tax_id.tax_rate) == "igv":
                            campo_15 = imp.amount_total

                # 16 Base imponible
                campo_16 = ""
                if inv.type_operation == "2":
                    campo_16 = inv.amount_untaxed

                # 17 Impuesto
                campo_17 = ""
                if inv.type_operation == "2":
                    campo_17 = inv.amount_tax

                # 18 Base imponible
                campo_18 = ""
                if inv.type_operation == "3":
                    campo_18 = inv.amount_untaxed

                # 19 Impuesto
                campo_19 = ""
                if inv.type_operation == "3":
                    campo_19 = inv.amount_tax

                # 20 -> Importe exonerado
                campo_20 = ""
                for line in inv.invoice_line_ids:
                    for imp in line.invoice_line_tax_ids:
                        if imp.name == "No gravado":
                            campo_20 = inv.amount_total

                # 21 -> Importe exonerado
                campo_21 = ""
                for imp in inv.tax_line_ids:
                    if str(imp.tax_id.tax_rate) == "isc":
                        campo_21 = imp.amount_total

                # 33 -> Tipo de Pago
                campo_33 = ""
                if inv.retencion == "ARET":
                    campo_33 = "ARET(Detección Automática Retención)"
                if inv.retencion == "SRET":
                    campo_33 = "SRET(Siempre Retención)"

                txt_line = "%s00|%s|M%s|%s|%s|%s|%s|%s|%s||%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%.2f|%s|%s|%s|" \
                           "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                               inv.move_id.date.strftime("%Y%m") or '',  # Periodo del Asiento -> 1
                               inv.move_id.name.replace("/", "") or '',  # Correlativo de Factura -> 2
                               str(correlativo).zfill(4) or '',
                               # Correlativo de todos los asientos no solo facturas -> 3
                               inv.date_invoice.strftime("%d/%m/%Y") or '',  # Fecha de la Factura -> 4
                               inv.date_due.strftime("%d/%m/%Y") or '',  # Fecha de Vencimiento -> 5
                               inv.document_type_id.number or '',  # N° del Tipo de Documento -> 6
                               str(inv.invoice_serie if inv.invoice_serie else 0).zfill(4),
                               # Numero de la Factura -> 7
                               inv.year_emission_dua or '',  # Año de emision del DUA -> 8
                               str(inv.invoice_number if inv.invoice_number else 0).zfill(8) or '',  # Numero -> 9
                               # Omitido -> 10
                               # N° Tipo de Documento Identidad -> 11
                               inv.partner_id.catalog_06_id.code or '',
                               inv.partner_id.vat or '',  # N° de Documento de Identidad -> 12
                               inv.partner_id.name or '',  # Nombre del Proveedor -> 13
                               campo_14 or '',  # Base imponible -> 14
                               campo_15 or "",  # Total -> 15
                               campo_16 or '',  # Base imponible -> 16
                               campo_17 or '',  # Impuesto -> 17
                               campo_18 or '',  # Base imponible -> 18
                               campo_19 or '',  # Impuesto -> 19
                               campo_20 or '',  # Total Adeudado -> 20
                               campo_21 or "",  # Impuesto -> 21
                               impuesto_otros or "",  # Otros de las Lineas -> 22
                               inv.amount_total or '',  # Total -> 23
                               inv.currency_id.name or '',  # Tipo de moneda -> 24
                               inv.exchange_rate or 0.00,  # Tipo de Cambio-> 25
                               campo_26 or '',  # Fecha del documento que modifica -> 26
                               # Tipo del documento que modifica -> 27
                               inv.refund_invoice_id.document_type_id.number or '',
                               # Numero del documento que modifica -> 28
                               inv.refund_invoice_id.invoice_number or '',
                               inv.refund_invoice_id.code_dua.number or '',  # Codigo DUA -> 29
                               inv.refund_invoice_id.invoice_number or '',  # Numero DUA -> 30
                               inv.date_detraction or '',  # Fecha de Detracciones -> 31
                               inv.num_detraction or '',  # Numero de Detracciones -> 32
                               campo_33 or '',  # Marca de Comprobante -> 33
                               inv.classifier_good.number or '',  # Clasificador de Bienes -> 34
                               '',  # -> 35
                               '',  # -> 36
                               '',  # -> 37
                               '',  # -> 38
                               '',  # -> 39
                               "1" if inv.state == 'paid' else "",  # -> 40
                           )
                content = content + "" + txt_line + "\r\n"
            self.write({
                'state': 'get',
                'txt_binary': base64.b64encode(content.encode('ISO-8859-1')),
                'txt_filename': "compras.txt"
            })
        if self.type == "out_invoice":
            for inv in invoice_ids:
                # Obtener el correlativo General de la Factura en el Mes
                correlativo = ""
                dominio = [('month_year_inv', 'like', inv.date_invoice.strftime("%m%Y"))]
                facturas = self.env['account.invoice'].search(dominio, order="id asc")
                contador = 0
                for inv in facturas:
                    contador = contador + 1
                    if inv.number == inv.number:
                        correlativo = "%s" % (contador)

                # 27 -> Fecha
                campo_27 = ""
                if inv.date_document != False:
                    campo_27 = inv.date_document.strftime("%d/%m/%Y")

                # 34 -> Fechas
                codigo_34 = ''
                if inv.date_invoice != False and inv.date_document != False:
                    if inv.date_invoice.strftime("%m%Y") == inv.date_document.strftime("%m%Y"):
                        codigo_34 = '1'
                    else:
                        if inv.date_invoice.strftime("%Y") != inv.date_document.strftime("%Y"):
                            codigo_34 = '9'
                        else:
                            if int(inv.date_invoice.strftime("%m")) == int(inv.date_document.strftime("%m")) - 1:
                                codigo_34 = '1'
                            else:
                                codigo_34 = '9'

                txt_line = "%s|%s|M%s|%s|%s|%s|%s|%s||%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%.2f|%s|%s|%s" \
                           "|%s|||%s|%s|" % (
                               inv.move_id.date and inv.move_id.date.strftime("%Y%m00") or '',
                               # Periodo del Asiento -> 1
                               inv.move_id.name.replace("/", "") or '',  # Correlativo de Factura -> 2
                               str(correlativo).zfill(4) or '',
                               # Correlativo de todos los asientos no solo facturas -> 3
                               inv.date_document and inv.date_document.strftime("%d/%m/%Y") or "",
                               # Fecha de Emisión -> 4
                               inv.date_due and inv.date_due.strftime("%d/%m/%Y") or '',  # Fecha de Vencimiento -> 5
                               inv.document_type_id.number or '',  # N° del Tipo de Documento -> 6
                               str(inv.invoice_serie if inv.invoice_serie else 0).zfill(4),  # Serie de Documento -> 7
                               inv.invoice_number or '',  # Numero de Documento -> 8
                               # Dejan en blanco -> 9
                               inv.partner_id.catalog_06_id.code or '',
                               # Tipo de Documento -> 10
                               inv.partner_id.vat or '',  # Numero de Documento -> 11
                               inv.partner_id.name or '',  # Nombre del Proveedor -> 12
                               # rec.total_exonerado or '',  # Factura de Exportacion -> 13
                               inv.inv_fac_exp or '',  # Factura de Exportacion -> 13
                               inv.inv_amount_untax or '',  # Impuesto no incluido -> 14
                               '' or '',  # Impuesto -> 15 - Dejar en Blanco
                               inv.amount_tax or '',  # Impuesto -> 16
                               '' or '',  # Impuesto -> 17 - Dejar en Blanco
                               inv.total_exonerado or '',  # Importe exonerado -> 18
                               inv.total_inafecto or '',  # Importe inafecto -> 19
                               inv.total_isc or '',  # Impuesto -> 20
                               '' or '',  # Base Imponible -> 21
                               '' or '',  # Impuesto -> 22
                               inv.inv_otros or '',  # Impuesto -> 23
                               inv.amount_total or '',  # Total -> 24
                               inv.currency_id.name or '',  # Tipo de moneda -> 25
                               inv.exchange_rate or 0.00,  # Tipo de Cambio-> 26
                               inv.refund_invoice_id.date_document and inv.refund_invoice_id.date_document.strftime(
                                   "%d/%m/%Y") or '',  # Fecha del Documento Asociado -> 27
                               inv.refund_invoice_id.document_type_id.number or '',  # Tipo del Documento Asociado -> 28
                               inv.refund_invoice_id.invoice_serie or '',  # Serie del Documento Asociado -> 29
                               inv.refund_invoice_id.invoice_number or '',  # Numero del Documento Asociado -> 30
                               # 2 campos en blanco -> 31, 32
                               "1" if inv.state == 'paid' else "",
                               codigo_34 or '',  # -> 34
                               # 1 campo en blanco -> 35
                           )
                content = content + "" + txt_line + "\r\n"
            self.write({
                'state': 'get',
                'txt_binary': base64.b64encode(content.encode('ISO-8859-1')),
                'txt_filename': "ventas.txt"
            })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generar TXT',
            'res_model': 'account.bill.txt',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
