# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import logging

_logger = logging.getLogger(__name__)


class detracciones(models.Model):
    _name = 'sunat.detracciones'
    _description = "Codigos de Detracciones"

    name = fields.Text(string="Description", translate=True)
    detrac = fields.Integer(string="Detraction", translate=True)
    detracmack = fields.Char(
        string="percentage", compute="_obtener_detraccion", translate=True)

    def _obtener_detraccion(self):
        for rec in self:
            detrac = str(rec.detrac)
            rec.detracmack = "{}%".format(detrac)


class document_type(models.Model):
    _name = 'sunat.document_type'
    _description = "Tipos de Documentos"

    name = fields.Text(compute="_document_type_full", store=True)
    number = fields.Char(string="Numero", size=2, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    @api.depends('number', 'description')
    @api.multi
    def _document_type_full(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class document_type_identity(models.Model):
    _name = 'sunat.document_type_identity'
    _description = "Tipos de Documentos de Identidad"

    name = fields.Text(compute="_document_type_identity_full", store=True)
    number = fields.Char(string="Numero", size=2, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    @api.depends('number', 'description')
    @api.multi
    def _document_type_identity_full(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class currency_type(models.Model):
    _name = 'sunat.currency_type'
    _description = "Tipos de Monedas"

    name = fields.Text(compute="_currency_type_full")
    number = fields.Char(string="Numero", size=2, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    def _currency_type_full(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class customs_code(models.Model):
    _name = 'sunat.customs_code'
    _description = "Codigos de Aduana"

    name = fields.Text(compute="_customs_code_full", store=True)
    number = fields.Char(string="Numero", size=3, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    @api.depends('number', 'description')
    @api.multi
    def _customs_code_full(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class classification_goods(models.Model):
    _name = 'sunat.classification_goods'
    _description = "Claseficación de Bienes"

    name = fields.Text(compute="_classification_goods_full", store=True)
    number = fields.Char(string="Numero", size=3, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    @api.depends('number', 'description')
    @api.multi
    def _classification_goods_full(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class Partner(models.Model):
    _inherit = 'res.partner'

    detrac_id = fields.Many2one('sunat.detracciones', 'Detraccion')

    document_type_identity_id = fields.Many2one(
        'sunat.document_type_identity', 'Tipo de Documento de Identidad')

    document_num_identity = fields.Char(string="Numero de Documento de Identidad")

    person_type = fields.Selection(string="Tipo de Persona", selection=[('01-Persona Natural', '01-Persona Natural'),
                                                                        ('02-Persona Jurídica', '02-Persona Jurídica'),
                                                                        ('03-Sujeto no Domiciliado',
                                                                         '03-Sujeto no Domiciliado')])


class res_partner_bank(models.Model):
    _inherit = 'res.partner.bank'

    is_detraction = fields.Boolean(string="Detracción")
    priority = fields.Integer(string="Prioridad")


class account_invoice(models.Model):
    _inherit = "account.invoice"
    # _rec_name = 'month_year_inv'

    # Detraction
    detrac_id = fields.Many2one('sunat.detracciones', 'Detraccion')
    # Value of the Detraction
    detraccion = fields.Monetary(string="Detraction Value", compute="_calcular_detrac", store=True)
    # Apply Retention
    apply_retention = fields.Boolean(string="Apply Retention")
    # Detraction Paid
    detraccion_paid = fields.Boolean(string="Detraction Paid", compute="_detraction_is_paid", store=True)
    #Saldo de Detraccion
    detraction_residual = fields.Monetary(string="Detraction To Pay", compute="_detraction_residual", store=True)
    # Total a Pagar
    total_pagar = fields.Monetary(string="Total a Pagar2", compute="_total_pagar_factura")
    # Numero de Factura del Proveedor
    invoice_number = fields.Char(string="Numero de Factura")

    # Campos necesarios para el TXT
    fourth_suspension = fields.Boolean(string="Suspencion de Cuarta")
    operation_type = fields.Selection(string="Tipo de Operación", selection=[('1.-Exportación', '1.-Exportación')])
    hide_dua_fields = fields.Boolean(compute="_hide_dua_fields")
    num_dua = fields.Char(string="N° DUA")
    year_emission_dua = fields.Char(string="Año de emisión de la DUA")

    # Document Type
    document_type_id = fields.Many2one('sunat.document_type', 'Document Type')
    currency_type_id = fields.Many2one('sunat.currency_type', 'Tipo de Moneda')

    # Detracciones
    date_detraction = fields.Date(string="Fecha de detracción")
    num_detraction = fields.Char(string="Número de detración")
    proof_mark = fields.Char(string="Marca del comprobante")
    classifier_good = fields.Many2one('sunat.classification_goods', 'Clasificación del Bien')

    # Documento que Modifica
    date_document_modifies = fields.Date(string="Fecha del documento que modifica")
    type_document_modifies_id = fields.Many2one('sunat.document_type', 'Tipo de Documento que Modifica')
    num_document_modifies = fields.Char(string="Numero del documento que modifica")
    num_dua_document_modifies = fields.Char(string="Número DUA")
    code_dua = fields.Many2one('sunat.customs_code', 'Código DUA')
    # Invoice
    series_document_modifies = fields.Char(string="Serie del documento que modifica")
    document_modify = fields.Boolean(string="Modifica Documento")

    # Factura de Cliente - Invoice
    export_invoice = fields.Boolean(string="Fac.- Exp.")
    exchange_rate = fields.Float(string="Tipo de Cambio")
    date_document = fields.Date(string="Fecha del Documento")

    # Hide or not Apply Retention
    hide_apply_retention = fields.Boolean(string='Hide', compute="_compute_hide_apply_retention")
    # Detraccion Aplica
    hide_detraction = fields.Boolean(compute="_compute_hide_detraction")

    # Para filtrar
    month_year_inv = fields.Char(
        compute="_get_month_invoice", store=True, copy=False)

    @api.depends('date_invoice')
    @api.multi
    def _get_month_invoice(self):
        for rec in self:
            if rec.date_invoice != False:
                rec.month_year_inv = rec.date_invoice.strftime("%m%Y")

    def _generate_txt_bill(self):
        content = ''
        for rec in self:
            # Obtener el correlativo General de la Factura en el Mes
            correlativo = ""
            dominio = [('month_year_inv', 'like', rec.date_invoice.strftime("%m%Y"))]
            facturas = self.env['account.invoice'].search(dominio, order="id asc")
            contador = 0
            for inv in facturas:
                contador = contador + 1
                if inv.number == rec.number:
                    correlativo = "%s" % (contador)

            # Obtener el impuesto otros
            impuesto_otros = ""
            for line in rec.invoice_line_ids:
                for imp in line.invoice_line_tax_ids:
                    if imp.name == "otros":
                        impuesto_otros = rec.amount_tax

            # 26 -> Fecha
            campo_26 = ""
            if rec.date_document_modifies != False:
                campo_26 = rec.date_document_modifies.strftime("%d/%m/%Y")

            content = "%s00|%s|M%s|%s|%s|%s|%s|%s|%s||%s|%s|%s|%s|%s|%s|%s|%s|%s|%s||%s|%s|%s|%.2f|%s|%s|%s|%s|" \
                      "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                          # Periodo del Asiento -> 1
                          rec.move_id.date.strftime("%Y/%m") or '',
                          # Correlativo de Factura -> 2
                          rec.move_id.name.replace("/", "") or '',
                          # Correlativo de todos los asientos no solo facturas -> 3
                          str(correlativo).zfill(4) or '',
                          # Fecha de la Factura -> 4
                          rec.date_invoice.strftime("%d/%m/%Y") or '',
                          # Fecha de Vencimiento -> 5
                          rec.date_due.strftime("%d/%m/%Y") or '',
                          rec.document_type_id.number or '',  # N° del Tipo de Documento -> 6
                          rec.number or '',  # Numero de la Factura -> 7
                          rec.year_emission_dua or '',  # Año de emision del DUA -> 8
                          rec.number[len(rec.number) - 4:len(rec.number)
                          ] or '',  # Numero -> 9
                          # Omitido -> 10
                          # N° Tipo de Documento Identidad -> 11
                          rec.partner_id.document_type_identity_id.number or '',
                          rec.partner_id.document_num_identity or '',  # N° de Documento de Identidad -> 12
                          rec.partner_id.name or '',  # Nombre del Proveedor -> 13
                          rec.amount_untaxed or '',  # Base imponible -> 14
                          rec.amount_total or '',  # Total -> 15
                          rec.amount_untaxed or '',  # Base imponible -> 16
                          rec.amount_tax or '',  # Impuesto -> 17
                          rec.amount_untaxed or '',  # Base imponible -> 18
                          rec.amount_tax or '',  # Impuesto -> 19
                          rec.residual or '',  # Total Adeudado -> 20
                          # Dejar en blando -> 21
                          impuesto_otros or '',  # Otros de las Lineas -> 22
                          rec.amount_total or '',  # Total -> 23
                          rec.currency_id.name or '',  # Tipo de moneda -> 24
                          rec.exchange_rate or 0.00,  # Tipo de Cambio-> 25
                          campo_26 or '',  # Fecha del documento que modifica -> 26
                          rec.type_document_modifies_id.number or '',  # Tipo del documento que modifica -> 27
                          rec.num_document_modifies or '',  # Numero del documento que modifica -> 28
                          rec.code_dua.number or '',  # Codigo DUA -> 29
                          rec.num_dua_document_modifies or '',  # Numero DUA -> 30
                          rec.date_detraction or '',  # Fecha de Detracciones -> 31
                          rec.num_detraction or '',  # Numero de Detracciones -> 32
                          rec.proof_mark or '',  # Marca de Comprobante -> 33
                          rec.classifier_good.number or '',  # Clasificador de Bienes -> 34
                          '',  # -> 35
                          '',  # -> 36
                          '',  # -> 37
                          '',  # -> 38
                          '',  # -> 39
                          '',  # -> 40
                      )
            return content

    def _generate_txt_invoice(self):
        content = "-"
        for rec in self:

            # Obtener el correlativo General de la Factura en el Mes
            correlativo = ""
            dominio = [('month_year_inv', 'like',
                        rec.date_invoice.strftime("%m%Y"))]
            facturas = self.env['account.invoice'].search(
                dominio, order="id asc")
            contador = 0
            for inv in facturas:
                contador = contador + 1
                if inv.number == rec.number:
                    correlativo = "%s" % (contador)

            # 13 -> Factura de Exportacion
            factura_exportacion = ""
            if rec.export_invoice == True:
                factura_exportacion = rec.amount_total

            # 14 -> Base imponible
            base_imponible_14 = ""
            for line in rec.invoice_line_ids:
                for imp in line.invoice_line_tax_ids:
                    if imp.name == "ISC":
                        base_imponible_14 = rec.amount_untaxed

            # 15 -> Impuesto
            impuesto_15 = ""
            for line in rec.invoice_line_ids:
                if rec.document_type_id.number == '07' and rec.document_modify == True:
                    if int(rec.date_invoice.strftime("%m")) > int(rec.date_document_modifies.strftime("%m")):
                        impuesto_15 = rec.amount_tax

            # 16 -> Impuesto
            impuesto_16 = ""
            for line in rec.invoice_line_ids:
                if rec.document_type_id.number == '07' and rec.document_modify == True:
                    if int(rec.date_invoice.strftime("%m")) == int(rec.date_document_modifies.strftime("%m")):
                        impuesto_16 = rec.amount_tax

            # 17 -> Impuesto
            impuesto_17 = ""
            for line in rec.invoice_line_ids:
                if rec.document_type_id.number == '07' and rec.document_modify == True:
                    if rec.date_invoice > rec.date_document_modifies:
                        impuesto_17 = rec.amount_tax

            # 18 -> Importe exonerado
            importe_exonerado_18 = ""
            for line in rec.invoice_line_ids:
                for imp in line.invoice_line_tax_ids:
                    if imp.name == "exonerado":
                        importe_exonerado_18 = rec.amount_total

            # 19 -> Importe inafecto
            importe_inafecto_19 = ""
            for line in rec.invoice_line_ids:
                for imp in line.invoice_line_tax_ids:
                    if imp.name == "inafecto":
                        importe_inafecto_19 = rec.amount_total

            # 20 -> Impuesto
            impuesto_20 = ""
            for line in rec.invoice_line_ids:
                for imp in line.invoice_line_tax_ids:
                    if imp.name == "ISC":
                        impuesto_20 = rec.amount_tax

            # 21 -> Base imponible
            base_imponible_21 = ""
            for line in rec.invoice_line_ids:
                for imp in line.invoice_line_tax_ids:
                    if imp.name == "arroz pilado":
                        base_imponible_21 = rec.amount_untaxed

            # 22 -> Impuesto
            impuesto_22 = ""
            for line in rec.invoice_line_ids:
                for imp in line.invoice_line_tax_ids:
                    if imp.name == "arroz pilado":
                        impuesto_22 = rec.amount_tax

            # 34 -> Fechas
            codigo_34 = ''
            if rec.date_invoice != False and rec.date_document != False:
                if rec.date_invoice.strftime("%m%Y") == rec.date_document.strftime("%m%Y"):
                    codigo_34 = '1'
                else:
                    if rec.date_invoice.strftime("%Y") != rec.date_document.strftime("%Y"):
                        codigo_34 = '9'
                    else:
                        if int(rec.date_invoice.strftime("%m")) == int(rec.date_document.strftime("%m")) - 1:
                            codigo_34 = '1'
                        else:
                            codigo_34 = '9'
            else:
                raise ValidationError("La factura " + rec.number + " no tiene todas las fechas")

            content = "%s|%s|%s|%s|%s|%s|%s|||%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%.2f|%s|%s|%s|%s||||%s|" % (
                rec.move_id.date.strftime("%Y%m") or '',  # Periodo del Asiento -> 1
                rec.move_id.name.replace("/", "") or '',  # Correlativo de Factura -> 2
                str(correlativo).zfill(4) or '',  # Correlativo de todos los asientos no solo facturas -> 3
                rec.date_invoice.strftime("%d/%m/%Y") or '',  # Fecha de la Factura -> 4
                rec.date_due.strftime("%d/%m/%Y") or '',  # Fecha de Vencimiento -> 5
                rec.document_type_id.number or '',  # N° del Tipo de Documento -> 6
                rec.number[len(rec.number) - 9:len(rec.number) - 5] or '',  # Numero de Documento -> 7
                # Dejan en blanco -> 8
                # Dejan en blanco -> 9
                rec.partner_id.document_type_identity_id.number or '',  # Validar el 10
                rec.number[len(rec.number) - 4:len(rec.number)] or '',  # Numero -> 11
                rec.partner_id.name or '',  # Nombre del Proveedor -> 12
                factura_exportacion or '',  # Factura de Exportacion -> 13
                base_imponible_14 or '',  # Base Imponible -> 14
                impuesto_15 or '',  # Impuesto -> 15
                impuesto_16 or '',  # Impuesto -> 16
                impuesto_17 or '',  # Impuesto -> 17
                importe_exonerado_18 or '',  # Importe exonerado -> 18
                importe_inafecto_19 or '',  # Importe inafecto -> 19
                impuesto_20 or '',  # Impuesto -> 20
                base_imponible_21 or '',  # Base Imponible -> 21
                impuesto_22 or '',  # Impuesto -> 22
                rec.amount_tax or '',  # Impuesto -> 23
                rec.amount_total or '',  # Total -> 24
                rec.currency_id.name or '',  # Tipo de moneda -> 25
                rec.exchange_rate or 0.00,  # Tipo de Cambio-> 26
                rec.date_document_modifies.strftime("%d/%m/%Y") or '',  # Fecha del Documento Asociado -> 27
                rec.type_document_modifies_id.number or '',  # Tipo del Documento Asociado -> 28
                rec.series_document_modifies or '',  # Serie del Documento Asociado -> 29
                rec.num_document_modifies or '',  # Numero del Documento Asociado -> 30
                # 3 campos en blanco -> 31, 32, 33
                codigo_34 or '',  # -> 34
                # 1 campo en blanco -> 35
            )
        return content

    # Method to hide Apply Retention
    @api.depends('document_type_id')
    @api.multi
    def _compute_hide_apply_retention(self):
        for rec in self:
            if rec.document_type_id.number == '02':
                rec.hide_apply_retention = False
            else:
                rec.hide_apply_retention = True

    @api.depends('document_type_id')
    @api.multi
    def _hide_dua_fields(self):
        for rec in self:
            if rec.document_type_id.number == '50':
                rec.hide_dua_fields = False
            else:
                rec.hide_dua_fields = True

    @api.depends('detrac_id')
    @api.multi
    def _compute_hide_detraction(self):
        for rec in self:
            if rec.detrac_id.name == 'No Aplica':
                rec.hide_detraction = True
            else:
                rec.hide_detraction = False

    @api.depends('detraccion', 'residual_signed', 'amount_total_signed')
    @api.multi
    def _detraction_is_paid(self):
        for rec in self:
            if rec.state == 'draft' or rec.hide_detraction == True:
                rec.detraccion_paid = False
            else:
                valor = rec.amount_total_signed - rec.residual_signed
                if valor >= (rec.detraccion) - 0.1:
                    rec.detraccion_paid = True
                else:
                    if rec.state == "Paid":
                        rec.detraccion_paid = True
                    else:
                        rec.detraccion_paid = False

    @api.depends('detraccion', 'residual_signed', 'amount_total_signed')
    @api.multi
    def _detraction_residual(self):
        for rec in self:
            if rec.state == 'draft' or rec.hide_detraction == True:
                rec.detraction_residual = 0
            else:
                valor = rec.amount_total_signed - rec.residual_signed
                rec.detraction_residual = rec.detraccion - valor
                if rec.detraction_residual < 0:
                    rec.detraction_residual = 0

    # Load the retention of the selected provider
    @api.onchange('partner_id')
    def _onchange_proveedor(self):
        # if len(self.detrac_id) <= 0 :
        self.detrac_id = self.partner_id.detrac_id

    # Calculate the value of the Detraction
    @api.depends('amount_total', 'detrac_id')
    @api.multi
    def _calcular_detrac(self):
        for rec in self:
            rec.detraccion = rec.amount_total * \
                                (rec.detrac_id.detrac / 100)

    # # Trial Action
    # @api.multi
    # def action_prueba(self):
    #     for rec in self:
    #         rec.reference = 'FacturaDePrueba'
    #     return True

    @api.depends('residual_signed', 'detraccion')
    @api.multi
    def _total_pagar_factura(self):
        for rec in self:
            if rec.detraccion_paid == True:
                rec.total_pagar = rec.residual_signed - rec.detraccion
                if rec.total_pagar < 0:
                    rec.total_pagar = 0
            else:
                rec.total_pagar = rec.residual_signed
