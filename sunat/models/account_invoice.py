# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


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
    # Saldo de Detraccion
    detraction_residual = fields.Monetary(string="Detraction To Pay", compute="_detraction_residual", store=True)
    # Total a Pagar
    total_pagar = fields.Monetary(string="Total a Pagar2", compute="_total_pagar_factura")
    # Numero de Factura del Proveedor
    invoice_number = fields.Char(string="Numero")
    invoice_serie = fields.Char(string="Serie")

    # Campos necesarios para el TXT
    fourth_suspension = fields.Boolean(string="Suspencion de Cuarta")
    operation_type = fields.Selection(string="Tipo de Operación", selection=[
        ('1.-Exportación', '1.-Exportación')])
    hide_dua_fields = fields.Boolean(compute="_hide_dua_fields")
    num_dua = fields.Char(string="N° DUA")
    year_emission_dua = fields.Char(string="Año de emisión de la DUA")

    # Document Type
    document_type_id = fields.Many2one('sunat.document_type', 'Tipo de Documento')
    type_income_id = fields.Many2one('sunat.type_income', 'Tipo de Renta')

    # Detracciones
    date_detraction = fields.Date(string="Fecha de detracción")
    num_detraction = fields.Char(string="Número de detración")
    proof_mark = fields.Char(string="Marca del comprobante")
    classifier_good = fields.Many2one(
        'sunat.classification_goods', 'Clasificación del Bien')

    # Documento que Modifica
    date_document_modifies = fields.Date(string="Fecha del documento que modifica")
    type_document_modifies_id = fields.Many2one('sunat.document_type', 'Tipo de Documento que Modifica')
    num_document_modifies = fields.Char(string="Numero del documento que modifica")
    num_dua_document_modifies = fields.Char(string="Número DUA")
    code_dua = fields.Many2one('sunat.customs_code', 'Código de la DUA')
    # code_dua = fields.Char(string="Código de la DUA")
    # Invoice
    series_document_modifies = fields.Char(string="Serie del documento que modifica")
    document_modify = fields.Boolean(string="Modifica Documento")

    # Factura de Cliente - Invoice
    export_invoice = fields.Boolean(string="Fac.- Exp.")
    exchange_rate = fields.Float(string="Tipo de Cambio", compute="_get_exchange_rate", store=True, copy=False)
    date_document = fields.Date(string="Fecha del Documento")

    # Hide or not Apply Retention
    hide_apply_retention = fields.Boolean(string='Hide', compute="_compute_hide_apply_retention")
    # Detraccion Aplica
    hide_detraction = fields.Boolean(compute="_compute_hide_detraction")

    retencion = fields.Selection(
        [('ARET', 'ARET(Detección Automática Retención)'),
         ('SRET', 'SRET(Siempre Retención)')],
        string='Tipo de Pago')

    # Datos del Proveedor
    type_ident = fields.Char(string='Documento', compute="_get_type_ident", copy=False)
    num_ident = fields.Char(string='Num. Documento', compute="_get_num_ident", copy=False)

    # Juego de Precios
    type_operation = fields.Selection(
        [('1', 'ADQ. GRAV, PARA OPERACIONES   GRAV. Y/O DE EXP-'),
         ('2', 'ADQ. GRAV. PARA OPE. GRAV. Y/O DE EXP.Y A OP. NO GRAV.'),
         ('3', 'ADQ. GRAV. PARA  OP-  NO GRAV.')],
        string='Tipo de Operación')
    base_imp = fields.Monetary(string="Base Imponible", compute="_base_imp")
    base_igv = fields.Monetary(string="IGV", compute="_base_igv")

    base_imp_ope_ex = fields.Monetary(string="B.Imp. Op.Ex", compute="_base_imp_ope_ex")
    base_igv_ope_ex = fields.Monetary(string="IGV. Op.Ex.", compute="_base_igv_ope_ex")

    base_imp_no_gra = fields.Monetary(string="B.I.  Dest.Op. no Grav.", compute="_base_imp_no_gra")
    base_igv_no_gra = fields.Monetary(string="Igv/des/op no Grav.", compute="_base_igv_no_gra")

    # Datos de Factura de Cliente
    inv_type_operation = fields.Selection(
        [('exonerado', 'Exonerado'), ('inafecto', 'Inafecto')],
        string='Tipo de Operación')

    inv_isc = fields.Monetary(string="ISC", compute="_inv_isc")
    inv_inafecto = fields.Monetary(string="Inafecto", compute="_inv_inafecto")
    inv_exonerada = fields.Monetary(string="Exonerada", compute="_inv_exonerada")
    inv_fac_exp = fields.Monetary(string="Valor fac de la exp", compute="_inv_fac_exp")
    inv_amount_untax = fields.Monetary(string="Impuesto no incluido", compute="_inv_amount_untax")

    inv_otros = fields.Char(string='Otros')

    inv_no_gravado = fields.Monetary(string="No Gravado", compute="_inv_no_gravado")

    # Para filtrar
    month_year_inv = fields.Char(compute="_get_month_invoice", store=True, copy=False)

    @api.multi
    @api.depends('currency_id')
    def _get_exchange_rate(self):
        for rec in self:
            rec.exchange_rate = rec.currency_id.rate_pe

    @api.multi
    def _inv_no_gravado(self):
        for rec in self:
            for line in rec.invoice_line_ids:
                for imp in line.invoice_line_tax_ids:
                    if imp.name == "No Gravado":
                        rec.inv_no_gravado = rec.amount_total

    @api.multi
    def _inv_isc(self):
        for rec in self:
            for line in rec.invoice_line_ids:
                for imp in line.invoice_line_tax_ids:
                    if imp.name == "ISC":
                        rec.inv_isc = rec.amount_tax

    @api.multi
    @api.depends('inv_type_operation')
    def _inv_inafecto(self):
        for rec in self:
            if rec.inv_type_operation == "inafecto":
                rec.inv_inafecto = rec.amount_untaxed

    @api.multi
    @api.depends('inv_type_operation')
    def _inv_exonerada(self):
        for rec in self:
            if rec.inv_type_operation == "exonerado":
                rec.inv_exonerada = rec.amount_untaxed

    @api.multi
    @api.depends('export_invoice')
    def _inv_fac_exp(self):
        for rec in self:
            if rec.export_invoice:
                rec.inv_fac_exp = rec.amount_untaxed

    @api.multi
    def _inv_amount_untax(self):
        for rec in self:
            if not (
                    rec.inv_isc or rec.inv_type_operation == "inafecto" or rec.inv_type_operation == "exonerado" or rec.export_invoice):
                rec.inv_amount_untax = rec.amount_untaxed

    @api.multi
    @api.depends('amount_untaxed', 'type_operation')
    def _base_imp(self):
        for rec in self:
            if (rec.type_operation == "1" or not rec.type_operation) and not rec.inv_no_gravado:
                rec.base_imp = rec.amount_untaxed

    @api.multi
    @api.depends('amount_untaxed', 'type_operation')
    def _base_igv(self):
        for rec in self:
            if (rec.type_operation == "1" and not rec.inv_isc) or (not rec.type_operation):
                rec.base_igv = rec.amount_tax

    @api.multi
    @api.depends('amount_untaxed', 'type_operation')
    def _base_imp_ope_ex(self):
        for rec in self:
            if rec.type_operation == "2":
                rec.base_imp_ope_ex = rec.amount_untaxed

    @api.multi
    @api.depends('amount_untaxed', 'type_operation')
    def _base_igv_ope_ex(self):
        for rec in self:
            if rec.type_operation == "2":
                rec.base_igv_ope_ex = rec.amount_tax

    @api.multi
    @api.depends('amount_untaxed', 'type_operation')
    def _base_imp_no_gra(self):
        for rec in self:
            if rec.type_operation == "3":
                rec.base_imp_no_gra = rec.amount_untaxed

    @api.multi
    @api.depends('amount_untaxed', 'type_operation')
    def _base_igv_no_gra(self):
        for rec in self:
            if rec.type_operation == "3":
                rec.base_igv_no_gra = rec.amount_tax

    @api.multi
    @api.depends('partner_id')
    def _get_type_ident(self):
        for rec in self:
            if rec.partner_id:
                rec.type_ident = rec.partner_id.catalog_06_id.name

    @api.multi
    @api.depends('partner_id')
    def _get_num_ident(self):
        for rec in self:
            if rec.partner_id:
                rec.num_ident = rec.partner_id.vat

    @api.multi
    @api.depends('date_invoice')
    def _get_month_invoice(self):
        for rec in self:
            if rec.date_invoice:
                rec.month_year_inv = rec.date_invoice.strftime("%m%Y")

    # Generar txt de Compra
    def _generate_txt_bill(self):
        content = ''
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

            # Obtener el impuesto otros
            impuesto_otros = ""
            for line in rec.invoice_line_ids:
                for imp in line.invoice_line_tax_ids:
                    if imp.name == "otros":
                        impuesto_otros = rec.amount_tax

            # 26 -> Fecha
            campo_26 = ""
            if rec.refund_invoice_id.date_document:
                campo_26 = rec.refund_invoice_id.date_document.strftime("%d/%m/%Y")

            # 14 Base imponible
            campo_14 = ""
            if rec.type_operation == "1":
                campo_14 = rec.amount_untaxed

            # 15 Impuesto
            campo_15 = ""
            if rec.type_operation == "1":
                campo_15 = rec.amount_tax

            # 16 Base imponible
            campo_16 = ""
            if rec.type_operation == "2":
                campo_16 = rec.amount_untaxed

            # 17 Impuesto
            campo_17 = ""
            if rec.type_operation == "2":
                campo_17 = rec.amount_tax

            # 18 Base imponible
            campo_18 = ""
            if rec.type_operation == "3":
                campo_18 = rec.amount_untaxed

            # 19 Impuesto
            campo_19 = ""
            if rec.type_operation == "3":
                campo_19 = rec.amount_tax

            # 20 -> Importe exonerado
            campo_20 = ""
            for line in rec.invoice_line_ids:
                for imp in line.invoice_line_tax_ids:
                    if imp.name == "No gravado":
                        campo_20 = rec.amount_total

            # 21 -> Importe exonerado
            campo_21 = ""
            for line in rec.invoice_line_ids:
                for imp in line.invoice_line_tax_ids:
                    if imp.name == "isc":
                        campo_21 = rec.amount_untaxed

            # 33 -> Tipo de Pago
            campo_33 = ""
            if rec.retencion == "ARET":
                campo_33 = "ARET(Detección Automática Retención)"
            if rec.retencion == "SRET":
                campo_33 = "SRET(Siempre Retención)"

            content = "%s00|%s|M%s|%s|%s|%s|%s|%s|%s||%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%.2f|%s|%s|%s|%s|" \
                      "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                          rec.move_id.date.strftime("%Y%m") or '',  # Periodo del Asiento -> 1
                          rec.move_id.name.replace("/", "") or '',  # Correlativo de Factura -> 2
                          str(correlativo).zfill(4) or '',  # Correlativo de todos los asientos no solo facturas -> 3
                          rec.date_invoice.strftime("%d/%m/%Y") or '',  # Fecha de la Factura -> 4
                          rec.date_due.strftime("%d/%m/%Y") or '',  # Fecha de Vencimiento -> 5
                          rec.document_type_id.number or '',  # N° del Tipo de Documento -> 6
                          str(rec.invoice_serie if rec.invoice_serie else 0).zfill(4),  # Numero de la Factura -> 7
                          rec.year_emission_dua or '',  # Año de emision del DUA -> 8
                          str(rec.invoice_number if rec.invoice_number else 0).zfill(8) or '',  # Numero -> 9
                          # Omitido -> 10
                          # N° Tipo de Documento Identidad -> 11
                          rec.partner_id.catalog_06_id.code or '',
                          rec.partner_id.vat or '',  # N° de Documento de Identidad -> 12
                          rec.partner_id.name or '',  # Nombre del Proveedor -> 13
                          campo_14 or '',  # Base imponible -> 14
                          campo_15 or '',  # Total -> 15
                          campo_16 or '',  # Base imponible -> 16
                          campo_17 or '',  # Impuesto -> 17
                          campo_18 or '',  # Base imponible -> 18
                          campo_19 or '',  # Impuesto -> 19
                          campo_20 or '',  # Total Adeudado -> 20
                          campo_21 or '',  # Impuesto -> 21
                          impuesto_otros or '',  # Otros de las Lineas -> 22
                          rec.amount_total or '',  # Total -> 23
                          rec.currency_id.name or '',  # Tipo de moneda -> 24
                          rec.exchange_rate or 0.00,  # Tipo de Cambio-> 25
                          campo_26 or '',  # Fecha del documento que modifica -> 26
                          # Tipo del documento que modifica -> 27
                          rec.refund_invoice_id.document_type_id.number or '',
                          # Numero del documento que modifica -> 28
                          rec.refund_invoice_id.invoice_number or '',
                          rec.refund_invoice_id.code_dua.number or '',  # Codigo DUA -> 29
                          rec.refund_invoice_id.invoice_number or '',  # Numero DUA -> 30
                          rec.date_detraction or '',  # Fecha de Detracciones -> 31
                          rec.num_detraction or '',  # Numero de Detracciones -> 32
                          campo_33 or '',  # Marca de Comprobante -> 33
                          rec.classifier_good.number or '',  # Clasificador de Bienes -> 34
                          '',  # -> 35
                          '',  # -> 36
                          '',  # -> 37
                          '',  # -> 38
                          '',  # -> 39
                          '',  # -> 40
                      )
            return content

    # Generar txt de Venta
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

            # 27 -> Fecha
            campo_27 = ""
            if rec.date_document != False:
                campo_27 = rec.date_document.strftime("%d/%m/%Y")

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

            content = "%s|%s|M%s|%s|%s|%s|%s|%s||%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%.2f|%s|%s|%s|%s" \
                      "||||%s|" % (
                          rec.move_id.date.strftime("%Y%m") or '',  # Periodo del Asiento -> 1
                          rec.move_id.name.replace("/", "") or '',  # Correlativo de Factura -> 2
                          str(correlativo).zfill(4) or '',  # Correlativo de todos los asientos no solo facturas -> 3
                          rec.date_invoice.strftime("%d/%m/%Y") or '',  # Fecha de la Factura -> 4
                          rec.date_due.strftime("%d/%m/%Y") or '',  # Fecha de Vencimiento -> 5
                          rec.document_type_id.number or '',  # N° del Tipo de Documento -> 6
                          str(rec.invoice_serie if rec.invoice_serie else 0).zfill(4),  # Serie de Documento -> 7
                          rec.invoice_number or '',  # Numero de Documento -> 8
                          # Dejan en blanco -> 9
                          rec.partner_id.catalog_06_id.code or '',
                          # Tipo de Documento -> 10
                          rec.partner_id.vat or '',  # Numero de Documento -> 11
                          rec.partner_id.name or '',  # Nombre del Proveedor -> 12
                          # rec.inv_exonerada or '',  # Factura de Exportacion -> 13
                          rec.inv_fac_exp or '',  # Factura de Exportacion -> 13
                          rec.inv_amount_untax or '',  # Impuesto no incluido -> 14
                          '' or '',  # Impuesto -> 15 - Dejar en Blanco
                          rec.amount_tax or '',  # Impuesto -> 16
                          '' or '',  # Impuesto -> 17 - Dejar en Blanco
                          rec.inv_exonerada or '',  # Importe exonerado -> 18
                          rec.inv_inafecto or '',  # Importe inafecto -> 19
                          rec.inv_isc or '',  # Impuesto -> 20
                          '' or '',  # Base Imponible -> 21
                          '' or '',  # Impuesto -> 22
                          rec.inv_otros or '',  # Impuesto -> 23
                          rec.amount_total or '',  # Total -> 24
                          rec.currency_id.name or '',  # Tipo de moneda -> 25
                          rec.exchange_rate or 0.00,  # Tipo de Cambio-> 26
                          campo_27 or '',  # Fecha del Documento Asociado -> 27
                          rec.refund_invoice_id.document_type_id.number or '',  # Tipo del Documento Asociado -> 28
                          rec.refund_invoice_id.invoice_serie or '',  # Serie del Documento Asociado -> 29
                          rec.refund_invoice_id.invoice_number or '',  # Numero del Documento Asociado -> 30
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
