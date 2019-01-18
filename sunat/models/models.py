# -*- coding: utf-8 -*-

from odoo import models, fields, api
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


class proveedor(models.Model):
    _inherit = "res.partner"

    detrac_id = fields.Many2one('sunat.detracciones', 'Detraccion')


class document_type(models.Model):
    _name = 'sunat.document_type'
    _description = "Tipos de Documentos"

    name = fields.Text(compute="_document_type_full")
    number = fields.Char(string="Numero", size=2, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    def _document_type_full(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class document_type_identity(models.Model):
    _name = 'sunat.document_type_identity'
    _description = "Tipos de Documentos de Identidad"

    name = fields.Text(compute="_document_type_identity_full")
    number = fields.Char(string="Numero", size=2, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

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

    name = fields.Text(compute="_customs_code_full")
    number = fields.Char(string="Numero", size=3, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    def _customs_code_full(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class classification_goods(models.Model):
    _name = 'sunat.classification_goods'
    _description = "Claseficación de Bienes"

    name = fields.Text(compute="_classification_goods_full")
    number = fields.Char(string="Numero", size=3, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    def _classification_goods_full(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class account_invoice(models.Model):
    _inherit = "account.invoice"

    # Detraction
    detrac_id = fields.Many2one('sunat.detracciones', 'Detraccion')
    # Value of the Detraction
    detraccion = fields.Monetary(
        string="Detraction Value", compute="_calcular_detrac", store=True)
    # Document Type
    document_type_id = fields.Many2one('sunat.document_type', 'Document Type')
    # Apply Retention
    apply_retention = fields.Boolean(string="Apply Retention")
    # Hide or not Apply Retention
    hide_apply_retention = fields.Boolean(
        string='Hide', compute="_compute_hide_apply_retention")
    # Detraction Paid
    detraccion_paid = fields.Boolean(
        string="Detraction Paid", compute="_detraction_is_paid", store=True)
    # Total a Pagar
    total_pagar = fields.Monetary(
        string="Total a Pagar2", compute="_total_pagar_factura")

    # Campos necesarios para el TXT
    operation_type = fields.Selection(string="Tipo de Operación", selection=[
        ('1.-Exportación', '1.-Exportación')])
    num_dua = fields.Char(string="N° DUA")
    year_emission_dua = fields.Char(string="Año de emisión de la DUA")
    document_type_identity_id = fields.Many2one('sunat.document_type_identity', 'Tipo de Documento de Identidad')
    document_num = fields.Integer(string="Numero de Documento")
    currency_type_id = fields.Many2one('sunat.currency_type', 'Tipo de Moneda')

    # Detracciones
    date_detraction = fields.Date(string="Fecha de detracción")
    num_detraction = fields.Char(string="Número de detración")
    proof_mark = fields.Char(string="Marca del comprobante")
    classifier_good = fields.Many2one('sunat.classification_goods', 'Clasificación del Bien')

    # Documento que Modifica
    date_document_modifies = fields.Date(string="Fecha del documento que modifica")
    type_document_modifies = fields.Many2one('sunat.document_type', 'Tipo de Documento que Modifica')
    num_document_modifies = fields.Char(
        string="Numero del documento que modifica")
    code_dua = fields.Many2one('sunat.customs_code', 'Código DUA')
    num_dua = fields.Char(string="Número DUA")

    # Para filtrar
    month_year_inv = fields.Char(compute="_get_month_invoice", store=True,copy=True)

    @api.depends('date_invoice')
    @api.multi
    def _get_month_invoice(self):
        for rec in self:
            rec.month_year_inv = rec.date_invoice.strftime("%m%Y")

    def _generate_txt_bill(self):
        content = '-'
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

            content = "%s00|%s|M%s|%s|%s|%s|%s|%s|%s||%s|%s|%s|%s|%s|%s|%s|%s|%s|%s||%s|%s|%s|%.2f|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                rec.move_id.date.strftime("%Y/%m") or '',  # Periodo del Asiento -> 1
                rec.move_id.name.replace("/", "") or '',  # Correlativo de Factura -> 2
                correlativo or '',  # Correlativo de todos los asientos no solo facturas -> 3
                rec.date_invoice.strftime("%d/%m/%Y") or '',  # Fecha de la Factura -> 4
                rec.date_due.strftime("%d/%m/%Y") or '',  # Fecha de Vencimiento -> 5
                rec.document_type_id.number or '',  # N° del Tipo de Documento -> 6
                rec.number or '',  # Numero de la Factura -> 7
                rec.year_emission_dua or '',  # Año de emision del DUA -> 8
                rec.number[len(rec.number) - 4:len(rec.number)] or '',  # Numero -> 9
                # Omitido -> 10
                rec.document_type_identity_id.number or '',  # N° Tipo de Documento Identidad -> 11
                rec.document_num or '',  # N° de Documento de Identidad -> 12
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
                rec.residual or '',  # Total Adeudado -> 23
                rec.currency_id.name or '',  # Tipo de moneda -> 24
                rec.currency_id.rate or '',  # -> 25
                rec.date_document_modifies or '',  # Fecha del documento que modifica -> 26
                rec.type_document_modifies.number or '',  # Tipo del documento que modifica -> 27
                rec.num_document_modifies or '',  # Numero del documento que modifica -> 28
                rec.code_dua.number or '',  # Codigo DUA -> 29
                rec.num_dua or '',  # Numero DUA -> 30
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
        content = '-'
        for rec in self:
            content = "%s|%s|" % (
                rec.move_id.date.strftime("%Y%m") or '',  # Periodo del Asiento -> 1
                rec.move_id.name.replace("/", "") or '',  # Correlativo de Factura -> 2
            )
            return content

    # Method to hide Apply Retention
    @api.depends('document_type_id')
    @api.multi
    def _compute_hide_apply_retention(self):
        for record in self:
            if record.document_type_id.number == '02':
                record.hide_apply_retention = False
            else:
                record.hide_apply_retention = True

    @api.depends('detraccion', 'residual_signed', 'amount_total_signed')
    @api.multi
    def _detraction_is_paid(self):
        for rec in self:
            # rec.detraccion_paid = True
            valor = rec.amount_total_signed - rec.residual_signed
            if valor >= rec.detraccion:
                rec.detraccion_paid = True
            else:
                if rec.state == "Paid":
                    rec.detraccion_paid = True
                else:
                    rec.detraccion_paid = False

    # Load the retention of the selected provider
    @api.onchange('partner_id')
    def _onchange_proveedor(self):
        # if len(self.detrac_id) <= 0 :
        self.detrac_id = self.partner_id.detrac_id

    # Calculate the value of the Detraction
    @api.depends('amount_total', 'detrac_id')
    @api.multi
    def _calcular_detrac(self):
        for record in self:
            record.detraccion = record.amount_total * \
                                (record.detrac_id.detrac / 100)

    # # Trial Action
    # @api.multi
    # def action_prueba(self):
    #     for rec in self:
    #         rec.reference = 'FacturaDePrueba'
    #     return True

    @api.depends('residual_signed', 'detraccion')
    @api.multi
    def _total_pagar_factura(self):
        for record in self:
            if record.detraccion_paid == True:
                record.total_pagar = record.residual_signed - record.detraccion
                if record.total_pagar < 0:
                    record.total_pagar = 0
            else:
                record.total_pagar = record.residual_signed
