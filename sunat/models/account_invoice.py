# -*- coding: utf-8 -*-

import json
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import logging
import requests
import qrcode
import base64
from io import BytesIO
from lxml.etree import SubElement, Element, tostring

_logger = logging.getLogger(__name__)


# Retorna las cabezeras de la peticion HTTP
def _get_headers(config):
    HEADERS = {
        'Authorization': config.api_token,
        'Content-Type': 'application/json'
    }
    return HEADERS


# Retorna las configuraciones del Sistema - Soporta MultiCompañia
def _get_config(self):
    config = self.env['res.config.settings'].sudo().search(
        [('company_id', '=', self._context.get('company_id', self.env.user.company_id.id))], order="id desc", limit=1)
    return config


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    # _rec_name = 'month_year_inv'
    _sql_constraints = [('unique_serie_number', 'unique(sunat_serie,sunat_number)',
                         'You cannot repeat a series and a correlative number.')]

    def _default_operation_type_id(self):
        return self.env['ir.model.data'].xmlid_to_res_id('sunat.nb_opetype_01') or False

    def _default_detrac_id(self):
        return self.env['ir.model.data'].xmlid_to_res_id('sunat.sunat_detrac_0')

    def _default_document_type_id(self):
        return self.env['ir.model.data'].xmlid_to_res_id('sunat.document_type_01')

    # Detraction
    detrac_id = fields.Many2one('sunat.detracciones', 'Detracción', default=_default_detrac_id)
    # Value of the Detraction
    detraccion = fields.Monetary(string="Detraction Value", compute="_calcular_detrac", store=True, copy=False)
    # Apply Retention
    apply_retention = fields.Boolean(string="Apply Retention")
    # Detraction Paid
    detraccion_paid = fields.Boolean(string="Detraction Paid", compute="_detraction_is_paid", store=True, copy=False)
    # Saldo de Detraccion
    detraction_residual = fields.Monetary(string="Detraction To Pay", compute="_detraction_residual", store=True,
                                          copy=False)
    # Total a Pagar
    total_pagar = fields.Monetary(string="Total a Pagar2", compute="_total_pagar_factura")

    # Numero de Factura del Proveedor
    invoice_number = fields.Char(string="Numero")
    invoice_serie = fields.Char(string="Serie")

    # Campos necesarios para el TXT
    fourth_suspension = fields.Boolean(string="Suspencion de Cuarta")
    operation_type = fields.Selection(string="Tipo de Operación", selection=[('1.-Exportación', '1.-Exportación')])
    hide_dua_fields = fields.Boolean(compute="_hide_dua_fields", copy=False)
    num_dua = fields.Char(string="N° DUA")
    year_emission_dua = fields.Char(string="Año de emisión de la DUA")

    # Document Type
    document_type_id = fields.Many2one('sunat.document_type', 'Tipo de Documento', default=_default_document_type_id)
    type_income_id = fields.Many2one('sunat.type_income', 'Tipo de Renta')

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
    code_dua = fields.Many2one('sunat.customs_code', 'Código de la DUA')
    # code_dua = fields.Char(string="Código de la DUA")
    # Invoice
    series_document_modifies = fields.Char(string="Serie del documento que modifica")
    document_modify = fields.Boolean(string="Modifica Documento")

    # Factura de Cliente - Invoice
    export_invoice = fields.Boolean(string="Fac.- Exp.")
    exchange_rate = fields.Float(string="Tipo de Cambio", digits=(12, 3), compute="_get_exchange_rate", store=True,
                                 copy=False)
    date_document = fields.Date(string="Fecha de Emisión", default=fields.Date.today(), copy=False)

    # Hide or not Apply Retention
    hide_apply_retention = fields.Boolean(string='Hide', compute="_compute_hide_apply_retention", copy=False)

    # Detraccion Aplica - False: Tiene Detraccion / True: No tiene Detraccion
    hide_detraction = fields.Boolean(compute="_compute_hide_detraction", copy=False)

    retencion = fields.Selection(
        [('ARET', 'ARET(Detección Automática Retención)'), ('SRET', 'SRET(Siempre Retención)')],
        string='Tipo de Pago')

    # Datos del Proveedor
    type_ident = fields.Char(string='Documento', related='partner_id.catalog_06_id.name')
    num_ident = fields.Char(string='Num. Documento', related='partner_id.vat')
    address = fields.Char(string='Dirección', related='partner_id.street')

    # Juego de Precios
    type_operation = fields.Selection(
        [('1', 'ADQ. GRAV, PARA OPERACIONES   GRAV. Y/O DE EXP-'),
         ('2', 'ADQ. GRAV. PARA OPE. GRAV. Y/O DE EXP.Y A OP. NO GRAV.'),
         ('3', 'ADQ. GRAV. PARA  OP-  NO GRAV.')],
        string='Tipo de Operación')

    type_operation_id = fields.Many2one('sunat.type_operation_detraction', 'Tipo de Operación de Detracción')
    code_goods_id = fields.Many2one('sunat.code_goods', 'Código de Bienes')
    payment_methods_id = fields.Many2one('sunat.payment_methods', 'Formas de Pago')
    perception_id = fields.Many2one('sunat.perception', 'Sujeto a Percepción')
    perception_value = fields.Monetary(string="Percepción", compute="_compute_amount", copy=False)

    base_imp = fields.Monetary(string="Base Imponible", compute="_base_imp", copy=False)
    base_igv = fields.Monetary(string="IGV", compute="_base_igv", copy=False)

    base_imp_ope_ex = fields.Monetary(string="B.Imp. Op.Ex", compute="_base_imp_ope_ex", copy=False)
    base_igv_ope_ex = fields.Monetary(string="IGV. Op.Ex.", compute="_base_igv_ope_ex", copy=False)

    base_imp_no_gra = fields.Monetary(string="B.I.  Dest.Op. no Grav.", compute="_base_imp_no_gra", copy=False)
    base_igv_no_gra = fields.Monetary(string="Igv/des/op no Grav.", compute="_base_igv_no_gra", copy=False)

    type_purchase = fields.Selection([
        ('01 Compra Interna', '01 Compra Interna'),
        ('02 Compra Externa', '02 Compra Externa')],
        string='Tipo de Compra')

    # Datos de Factura de Cliente
    inv_type_operation = fields.Selection([
        ('1', 'Operación gravada con el IGV'),
        ('2', 'Operación no gravada con el IGV'),
        ('3', 'Mixto')
    ], string='Tipo de Operación')

    # Asiento Castigo
    move_punishment_id = fields.Many2one('account.move', "Asiento Castigo")

    # Taxs
    total_isc = fields.Monetary(string="Total ISC", compute="_compute_total_isc", copy=False)
    total_igv = fields.Monetary(string="Total IGV", compute="_compute_total_igv", copy=False)
    total_otros = fields.Monetary(string="Total Otros", compute="_compute_total_otros", copy=False)
    total_inafecto = fields.Monetary(string="Total Inafecto", compute="_compute_total_inafecto", copy=False)
    total_exonerado = fields.Monetary(string="Total Exonerado", compute="_compute_total_exonerado", copy=False)
    total_no_gravado = fields.Monetary(string="Total No Gravado", compute="_compute_total_no_gravado", copy=False)

    total_discount = fields.Monetary(string="Total Discount", compute="_compute_total_discount", copy=False)

    credit_note_type_id = fields.Many2one('einvoice.catalog.09', string='Credit note type',
                                          help='Catalog 09: Type of Credit note')
    operation_type_id = fields.Many2one('nubefact.operation_type', string='Tipo de Operación',
                                        help='Tipo de Operación', default=_default_operation_type_id)

    # Factura Cliente
    inv_fac_exp = fields.Monetary(string="Valor fac de la exp", compute="_inv_fac_exp", copy=False)
    inv_amount_untax = fields.Monetary(string="Impuesto no incluido", compute="_inv_amount_untax", copy=False)
    inv_otros = fields.Char(string='Otros')

    # Factura Proveedor
    num_comp_serie = fields.Char(string='Numero de Comp. N1 de Serie')
    num_perception = fields.Char(string='Numero de Percepción')

    is_paid = fields.Boolean(string="Tiene Pago", compute="_compute_is_paid", store=True, copy=False)

    # Campo para guardar respuesta de sunat
    sunat_response = fields.Text(string="Respuesta de Sunat", readonly=True, copy=False)
    sunat_request = fields.Text(string="Solicitud a Sunat", readonly=True, copy=False)
    sunat_status = fields.Selection([
        ('-', 'Pendiente de Envío'),
        ('0', 'Aceptado'),
        ('1', 'Rechazado'),
        ('2', 'Anulado'),
        ('3', 'Error'),
        ('4', 'No recibido por Sunat'),
        ('5', 'Anulacion no Recibida por Sunat')
    ], string='Estado Sunat', help='Estado del Documento en Sunat',
        default='-', readonly=True, copy=False)
    sunat_description = fields.Text(string="Mensaje de Sunat", readonly=True, copy=False)
    sunat_qr_code = fields.Binary(string="QR de Sunat", copy=False)
    sunat_pdf = fields.Binary(string="PDF de Sunat", copy=False)
    electronic_invoicing = fields.Boolean(string="Electronic Invoicing Peru",
                                          related="company_id.electronic_invoicing",
                                          store=True)

    # 0003 - Inicio
    sunat_serie = fields.Many2one(comodel_name='sunat.series', string='Serie', required=True, ondelete="restrict")
    sunat_number = fields.Char(string="Numero", store=True, readonly=True, copy=False)
    sunat_document_number = fields.Char(string="Numero de Documento",
                                        compute="_compute_document_number",
                                        store=True, copy=False)
    # 0003 - Fin

    # Para filtrar
    month_year_inv = fields.Char(compute="_get_month_invoice", store=True, copy=False)

    @api.constrains('invoice_line_ids')
    def _check_lines(self):
        if self.type in 'out_invoice,out_refund':
            for line in self.invoice_line_ids:
                if line.product_id and not line.product_id.sunat_product_id:
                    raise ValidationError("El producto " + str(line.product_id.name) +
                                          " no tiene registrado su codigo de producto Sunat")

    @api.constrains('sunat_serie', 'document_type_id')
    def _check_sunat_serie(self):
        if self.type in 'out_invoice,out_refund':
            if self.sunat_serie and self.document_type_id:
                if not self.sunat_serie.sequence_id:
                    raise ValidationError("Se necesita una Serie que tenga una Secuencia")
                else:
                    if self.document_type_id.number in '01,03,07,08':
                        if len(self.sunat_serie.name) > 4:
                            raise ValidationError("La serie tiene que ser un maximo de 4 Caracteres")
                    elif self.document_type_id.number in '12':
                        if len(self.sunat_serie.name) > 20:
                            raise ValidationError("La serie tiene que ser un maximo de 20 Caracteres")

    @api.constrains('partner_id')
    def _check_partner(self):
        if self.partner_id:
            if not self.partner_id.vat or not self.partner_id.catalog_06_id:
                raise ValidationError("Tiene que llenar el Tipo de Documento de Identidad y su Valor")

    # Cargar la Detraccion del Proveedor
    @api.onchange('partner_id')
    def _onchange_proveedor(self):
        if self.partner_id:
            self.detrac_id = self.partner_id.detrac_id

    # Cambiar el tipo de Operacion cuando tiene detracción
    @api.onchange('detrac_id')
    def _onchange_detrac_id(self):
        if self.detrac_id and not self.detrac_id.name == 'No Aplica':
            self.operation_type_id = self.env['ir.model.data'].xmlid_to_res_id('sunat.nb_opetype_30') or False
        else:
            self.operation_type_id = self.env['ir.model.data'].xmlid_to_res_id('sunat.nb_opetype_01') or False

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id.sunat_serie_id:
            self.sunat_serie = self.journal_id.sunat_serie_id

    # 0002 - Incio - Modificado
    @api.multi
    @api.depends('currency_id', 'date_document')
    def _get_exchange_rate(self):
        for rec in self:
            currency = False
            if rec.date_document:
                domain = [('currency_id.id', '=', rec.currency_id.id),
                          ('name', '=', fields.Date.to_string(rec.date_document)),
                          ('currency_id.type', '=', rec.currency_id.type)]
                currency = self.env['res.currency.rate'].search(domain, limit=1)
            if currency:
                rec.exchange_rate = currency.rate_pe
            else:
                if rec.currency_id:
                    rec.exchange_rate = rec.currency_id.rate_pe
        # 0002 - Fin - Modificado

    # 0003 - Inicio
    @api.multi
    def action_invoice_open(self):
        # OVERRIDE
        # Auto-reconcile the invoice with payments coming from transactions.
        # It's useful when you have a "paid" sale order (using a payment transaction) and you invoice it later.
        res = super(AccountInvoice, self).action_invoice_open()

        config = _get_config(self)

        if self.journal_id.sunat_serie_id and not self.sunat_serie:
            self.sunat_serie = self.journal_id.sunat_serie_id

        if self.sunat_serie.sequence_id:
            seq = self.sunat_serie.sequence_id
            number = seq._next_do()
            if number:
                self.sunat_number = number
                if config.electronic_invoicing:
                    resp = self.report_sunat(config)
                    if not resp:
                        seq.number_next = int(number)
                        raise ValidationError("No se pudo validar el documento en Sunat")
        return res
        # 0003 - Fin

    @api.multi
    @api.depends('sunat_serie', 'sunat_number')
    def _compute_document_number(self):
        for rec in self:
            name = ""
            if rec.sunat_serie:
                name = name + str(rec.sunat_serie.name)
            if rec.sunat_number:
                name = name + "-" + str(rec.sunat_number)
            rec.sunat_document_number = name

    @api.multi
    @api.depends('payment_ids')
    def _compute_is_paid(self):
        for rec in self:
            if len(rec.payment_ids) > 0:
                rec.is_paid = True
            else:
                rec.is_paid = False

    @api.one
    def _compute_total_isc(self):
        taxes = list(filter(lambda line: not line.tax_id.tax_rate != 'isc', self.tax_line_ids))
        self.total_isc = sum(line.amount_total for line in taxes)

    @api.one
    def _compute_total_igv(self):
        taxes = list(filter(lambda line: not line.tax_id.tax_rate != 'igv', self.tax_line_ids))
        self.total_igv = sum(line.amount_total for line in taxes)

    @api.one
    def _compute_total_otros(self):
        taxes = list(filter(lambda line: not line.tax_id.tax_rate != 'otros', self.tax_line_ids))
        self.total_no_gravado = sum(line.amount_total for line in taxes)

    @api.one
    def _compute_total_inafecto(self):
        taxes = list(filter(lambda line: not line.tax_id.tax_rate != 'inafecto', self.tax_line_ids))
        self.total_inafecto = self.amount_untaxed if len(taxes) >= 1 else 0.0

    @api.one
    def _compute_total_exonerado(self):
        taxes = list(filter(lambda line: not line.tax_id.tax_rate != 'exonerado', self.tax_line_ids))
        self.total_exonerado = self.amount_untaxed if len(taxes) >= 1 else 0.0

    @api.one
    def _compute_total_no_gravado(self):
        taxes = list(filter(lambda line: not line.tax_id.tax_rate != 'no_gravado', self.tax_line_ids))
        self.total_no_gravado = self.amount_untaxed if len(taxes) >= 1 else 0.0

    @api.one
    def _compute_total_discount(self):
        self.total_discount = sum(line.total_discount for line in self.invoice_line_ids)

    @api.multi
    @api.depends('export_invoice')
    def _inv_fac_exp(self):
        for rec in self:
            if rec.export_invoice:
                rec.inv_fac_exp = rec.amount_untaxed_invoice_signed

    @api.multi
    def _inv_amount_untax(self):
        for rec in self:
            if not (
                    rec.total_isc or rec.inv_type_operation == "inafecto" or rec.inv_type_operation == "exonerado" or rec.export_invoice):
                rec.inv_amount_untax = rec.amount_untaxed_invoice_signed  # amount_untaxed -> Para factura de Cliente

    @api.multi
    @api.depends('amount_untaxed', 'type_operation')
    def _base_imp(self):
        for rec in self:
            if (rec.type_operation == "1" or not rec.type_operation) and not rec.total_no_gravado:
                rec.base_imp = rec.amount_untaxed

    @api.multi
    @api.depends('amount_untaxed', 'type_operation')
    def _base_igv(self):
        for rec in self:
            if (rec.type_operation == "1" and not rec.total_isc) or (not rec.type_operation):
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
    @api.depends('date_invoice')
    def _get_month_invoice(self):
        for rec in self:
            if rec.date_invoice:
                rec.month_year_inv = rec.date_invoice.strftime("%m%Y")

    # Method to hide Apply Retention
    @api.depends('document_type_id')
    @api.multi
    def _compute_hide_apply_retention(self):
        for rec in self:
            if rec.document_type_id.number == '02':
                rec.hide_apply_retention = False
            else:
                rec.hide_apply_retention = True

    @api.one
    @api.depends('document_type_id')
    def _hide_dua_fields(self):
        if self.document_type_id.number == '50':
            self.hide_dua_fields = False
        else:
            self.hide_dua_fields = True

    @api.depends('detrac_id')
    @api.multi
    def _compute_hide_detraction(self):
        for rec in self:
            if rec.detrac_id.name == 'No Aplica' or not rec.detrac_id:
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

    # Calculate the value of the Detraction
    @api.depends('amount_total', 'detrac_id')
    @api.multi
    def _calcular_detrac(self):
        for rec in self:
            rec.detraccion = rec.amount_total * (rec.detrac_id.detrac / 100)

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

    # Reemplazamos un metodo de odoo para agregar la Percepcion
    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type', 'perception_id')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)

        self.amount_total = self.amount_untaxed + self.amount_tax + self.perception_value
        self.perception_value = self.amount_total * (self.perception_id.percentage / 100)

        self.amount_total = self.amount_total + self.perception_value
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id
            amount_total_company_signed = currency_id._convert(self.amount_total, self.company_id.currency_id,
                                                               self.company_id,
                                                               self.date_invoice or fields.Date.today())
            amount_untaxed_signed = currency_id._convert(self.amount_untaxed, self.company_id.currency_id,
                                                         self.company_id, self.date_invoice or fields.Date.today())
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    @api.multi
    def _punishment(self):
        for rec in self:
            if rec.state != 'open':
                raise ValidationError('La factura ' + str(rec.number) + ' no esta abierta')

            if rec.move_punishment_id:
                raise ValidationError('La factura ' + str(rec.number) + ' ya tiene un catigo')

            move_line = False
            for line in rec.move_id.line_ids:
                if str(line.account_id.code) == '121100' and not move_line:
                    move_line = line

            if not move_line:
                raise ValidationError('No se encontro la cuenta 121100 en el asiento de factura')

            # Lista de Lineas
            lines = []

            # Linea 2
            account_2 = self.env['account.account'].search([('code', '=', '684110')])
            if account_2:
                lines.append((0, 0, {
                    'account_id': account_2 and account_2.id or False,
                    'debit': move_line.debit
                }))
            else:
                raise ValidationError('No se encontro la cuenta 684110')

            # Linea 1
            account_1 = self.env['account.account'].search([('code', '=', '191100')])
            if account_1:
                lines.append((0, 0, {
                    'account_id': account_1 and account_1.id or False,
                    'credit': move_line.debit
                }))
            else:
                raise ValidationError('No se encontro la cuenta 191100')

            # Asiento
            account_move_dic = {
                'date': str(datetime.now().date()) or False,
                'journal_id': move_line.journal_id and move_line.journal_id.id or False,
                'ref': 'Por el castigo de la factura ' + str(rec.number),
                'invoice_id': rec and rec.id or False,
                'line_ids': lines
            }

            move_punishment = self.env['account.move'].create(account_move_dic)
            move_punishment.post()

            rec.move_punishment_id = move_punishment
        return True

    # 0004 - Inicio
    @api.multi
    def anular_sunat(self, reason, config=False):
        if not config:
            config = _get_config(self)
        data = {}
        data['operacion'] = 'generar_anulacion'
        data['tipo_de_comprobante'] = 1
        data['serie'] = self.sunat_serie.name if self.sunat_serie else ""
        data['numero'] = self.sunat_number if self.sunat_serie else ""
        data['motivo'] = reason if reason else ""
        data['codigo_unico'] = self.id
        response = requests.post(url=config.api_url, headers=_get_headers(config), json=data)
        if response.status_code == 200:
            resp = response.json()
            if resp['aceptada_por_sunat']:
                self.sunat_status = '2'
                return True
            else:
                self.sunat_status = '5'
                return self.sunat_check_status(config)
        else:
            return False

    @api.multi
    def sunat_check_status(self, config=False):
        if not config:
            config = _get_config(self)
        data = {}
        data['operacion'] = 'consultar_anulacion'
        data['tipo_de_comprobante'] = 1
        data['serie'] = self.sunat_serie.name if self.sunat_serie else ""
        data['numero'] = self.sunat_number if self.sunat_serie else ""
        if self.sunat_status == '5':
            response = requests.post(url=config.api_url, headers=_get_headers(config), json=data)
            if response.status_code == 200:
                resp = response.json()
                if resp['aceptada_por_sunat']:
                    self.sunat_status = '2'
                    return True
                else:
                    self.sunat_status = '5'
                    return False
            else:
                return False

    @api.multi
    def report_sunat(self, config=False):
        respuesta = False
        if not config or self.type == "out_refund":
            config = _get_config(self)
        #  --  JSON  --
        data = {}
        seq = False
        number = 0
        if self.sunat_serie.sequence_id and not self.sunat_number:
            seq = self.sunat_serie.sequence_id
            number = seq._next_do()
            if number:
                self.sunat_number = number
        if number == 0:
            number = self.sunat_number
        if config.electronic_invoicing:
            documentos = {
                'out_invoice': 1,  # FACTURA / Customer Invoice
                'out_refund': 3,  # NOTA DE CRÉDITO / Customer Credit Note
            }
            data['operacion'] = 'generar_comprobante'
            data['tipo_de_comprobante'] = documentos.get(self.type, 0)
            data['serie'] = self.sunat_serie.name if self.sunat_serie else ""
            data['numero'] = self.sunat_number if self.sunat_serie and self.sunat_number else ""
            data['sunat_transaction'] = int(self.operation_type_id.code) if self.operation_type_id.code else ""
            data['cliente_tipo_de_documento'] = \
                int(self.partner_id.catalog_06_id.code) if self.partner_id.catalog_06_id else ""
            data['cliente_numero_de_documento'] = int(self.partner_id.vat) if self.partner_id.vat else ""
            data['cliente_denominacion'] = \
                self.partner_id.registration_name if self.partner_id.registration_name else ""
            data['cliente_direccion'] = self.partner_id.street if self.partner_id.street else ""
            data['cliente_email'] = self.partner_id.email if self.partner_id.email else ""
            data['cliente_email_1'] = ""
            data['cliente_email_2'] = ""
            data['fecha_de_emision'] = self.date_document.strftime("%d-%m-%Y") if self.date_document else ""
            data['fecha_de_vencimiento'] = self.date_due.strftime("%d-%m-%Y") if self.date_due else ""
            monedas = {
                'PEN': 1,
                'USD': 2,
                'EUR': 3
            }
            data['moneda'] = monedas.get(self.currency_id.name, "") if self.currency_id else ""
            data['tipo_de_cambio'] = self.exchange_rate if self.exchange_rate and self.exchange_rate != 1.0 else ""
            porcentaje_de_igv = ""
            taxes = list(filter(lambda line: not line.tax_id.tax_rate != 'igv', self.tax_line_ids))
            if len(taxes) > 0:
                porcentaje_de_igv = taxes[0].tax_id.amount
            data['porcentaje_de_igv'] = "18.00"
            data['descuento_global'] = ""
            data['total_descuento'] = round(self.total_discount, 10) if self.total_discount else ""
            data['total_anticipo'] = ""
            data['total_gravada'] = round(self.amount_untaxed, 10) if self.total_igv else ""
            data['total_inafecta'] = round(self.total_inafecto, 10) if self.total_inafecto else ""
            data['total_exonerada'] = round(self.total_exonerado, 10) if self.total_exonerado else ""
            if self.total_isc:
                data['total_isc'] = round(self.total_isc, 10) if self.total_isc else ""
            data['total_igv'] = round(self.total_igv, 10) if self.total_igv else ""
            data['total_gratuita'] = ""
            data['total_otros_cargos'] = round(self.inv_otros, 10) if self.inv_otros else ""
            data['total'] = round(self.amount_total, 10) if self.amount_total else ""
            data['percepcion_tipo'] = ""
            data['percepcion_base_imponible'] = ""
            data['total_percepcion'] = ""
            data['total_incluido_percepcion'] = ""
            data['detraccion'] = not self.hide_detraction
            data['observaciones'] = ""
            data['documento_que_se_modifica_tipo'] = documentos.get(self.refund_invoice_id.type, 0)
            data['documento_que_se_modifica_serie'] = self.refund_invoice_id.sunat_serie.name \
                if self.refund_invoice_id.sunat_serie.name else ""
            data['documento_que_se_modifica_numero'] = self.refund_invoice_id.sunat_number \
                if self.refund_invoice_id.sunat_serie and self.refund_invoice_id.sunat_number else ""
            data['tipo_de_nota_de_credito'] = 1 if self.type == 'out_refund' else ""
            data['tipo_de_nota_de_debito'] = ""
            data['enviar_automaticamente_a_la_sunat'] = True
            data['enviar_automaticamente_al_cliente'] = False
            data['codigo_unico'] = self.id
            data['condiciones_de_pago'] = self.payment_term_id.name if self.payment_term_id else ""
            data['medio_de_pago'] = ""
            data['placa_vehiculo'] = ""
            data['orden_compra_servicio'] = self.origin if self.origin else ""
            if not self.hide_detraction:
                data['detraccion_tipo'] = float(self.detrac_id.number) if self.detrac_id.number else ""
                data['detraccion_total'] = self.detraccion if self.detraccion else ""
            data['tabla_personalizada_codigo'] = ""
            data['formato_de_pdf'] = ""
            data['generado_por_contingencia'] = ""
            data['items'] = []
            # data['guias'] = []

            numorden = 0
            for line in self.invoice_line_ids:
                item = {}
                item['unidad_de_medida'] = line.uom_id.sunat_code if line.uom_id.sunat_code else ""
                item['codigo'] = ""  # str(numorden).zfill(4)
                item['descripcion'] = str(line.product_id.name) if line.product_id else ""
                item['cantidad'] = line.quantity
                item['valor_unitario'] = round(line.price_unit, 10)
                item['precio_unitario'] = round((line.total_without_discount) / line.quantity, 10)
                item['descuento'] = round(line.total_discount, 10) if line.total_discount else ""
                item['subtotal'] = round(line.price_subtotal, 10)
                if line.total_isc and line.isc_type:
                    item['tipo_de_isc'] = line.isc_type if line.isc_type else ""
                    item['isc'] = round(line.total_isc, 10) if line.total_isc else 0
                item['tipo_de_igv'] = line.igv_type if line.igv_type else ""
                item['igv'] = round(line.total_igv, 10) if line.total_igv else 0
                item['total'] = round(line.price_total, 10)
                item['anticipo_regularizacion'] = False
                item['anticipo_documento_serie'] = ""
                item['anticipo_documento_numero'] = ""
                item['codigo_producto_sunat'] = line.product_id.sunat_product_id.code \
                    if line.product_id.sunat_product_id.code else ""
                data['items'].append(item)

            _logger.info("\n" + json.dumps(data, indent=3))

        # Realizamos la peticion HTTP y obtenemos la respuesta
        response = requests.post(url=config.api_url, headers=_get_headers(config), json=data)
        # response = requests.get(url)
        _logger.info(response.json())
        # Si la Respuesta es Correcta
        if response.status_code == 200:
            resp = response.json()
            if resp['cadena_para_codigo_qr'] and resp['enlace_del_pdf'] and resp['codigo_hash']:
                # Inicio - Generamos el codigo qr
                qr_code = qrcode.make(resp['cadena_para_codigo_qr'])
                buffered = BytesIO()
                qr_code.save(buffered, format="JPEG")
                qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                # Fin - Generamos el codigo qr
                if resp['aceptada_por_sunat']:
                    sunat_status = "0"
                elif not resp['aceptada_por_sunat']:
                    sunat_status = "4"
                else:
                    sunat_status = "3"
                self.sunat_response = json.dumps(resp)
                self.sunat_request = json.dumps(data)
                self.sunat_status = sunat_status
                self.sunat_description = resp['sunat_description']
                self.sunat_qr_code = qr_base64
                respuesta = True
        elif response.status_code == 400:
            resp = response.json()
            self.sunat_response = json.dumps(resp)
            self.sunat_status = '1'
            self.sunat_request = json.dumps(data)
            if resp['errors']:
                raise ValidationError(resp['errors'])
            if resp['sunat_soap_error']:
                raise ValidationError(resp['sunat_soap_error'])
            respuesta = True
        else:
            self.sunat_response = str(response)
            self.sunat_status = '3'
            self.sunat_request = json.dumps(data)
        if self.sunat_status != '0' and self.sunat_status != '4':
            seq.number_next = int(number)
            self.sunat_number = 0
        return respuesta
        # 0004 - Inicio


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    # Facturación Electronica
    total_discount = fields.Monetary(string="Total Discount", compute="_compute_total_discount", copy=False)
    total_without_discount = fields.Monetary(string="Tax Without Discount", compute="_compute_total_discou", copy=False)
    total_isc = fields.Monetary(string="Total ISC", compute="_compute_total_discou", copy=False)
    total_igv = fields.Monetary(string="Total IGV", compute="_compute_total_discou", copy=False)
    igv_type = fields.Char(string="IGV type", compute="_compute_igv_type", copy=False)
    isc_type = fields.Char(string="ISC type", compute="_compute_igv_type", copy=False)

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity', 'product_id', 'invoice_id.partner_id',
                 'invoice_id.currency_id', 'invoice_id.company_id', 'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_total_discou(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit - (self.price_unit * ((self.discount or 0.0) / 100.0))
        taxes_without_discount = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity,
                                                          product=self.product_id,
                                                          partner=self.invoice_id.partner_id)
            taxes_without_discount = self.invoice_line_tax_ids.compute_all(self.price_unit, currency, self.quantity,
                                                                           product=self.product_id,
                                                                           partner=self.invoice_id.partner_id)
            igv = 0
            isc = 0
            for tax in taxes['taxes']:
                if tax.get('type', '') == 'igv':
                    igv = igv + tax['amount']
                if tax.get('type', '') == 'isc':
                    isc = isc + tax['amount']
            self.total_igv = igv
            self.total_isc = isc
        self.total_without_discount = taxes_without_discount['total_included'] \
            if taxes_without_discount else self.quantity * self.price_unit
        price = self.price_unit * ((self.discount or 0.0) / 100.0)
        discount = self.quantity * price
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            currency = self.invoice_id.currency_id
            date = self.invoice_id._get_currency_rate_date()
            discount = currency._convert(discount,
                                         self.invoice_id.company_id.currency_id,
                                         self.company_id or self.env.user.company_id,
                                         date or fields.Date.today())
        self.total_discount = discount

    @api.one
    def _compute_igv_type(self):
        inafecto = list(filter(lambda line: not line.tax_rate != 'inafecto', self.invoice_line_tax_ids))
        exonerado = list(filter(lambda line: not line.tax_rate != 'exonerado', self.invoice_line_tax_ids))
        isc = list(filter(lambda line: not line.tax_rate != 'isc', self.invoice_line_tax_ids))
        if len(inafecto) >= 1:
            self.igv_type = '9'  # Gravado - Operación Onerosa
        elif len(exonerado) >= 1:
            self.igv_type = '8'  # Exonerado - Operación Onerosa
        else:
            self.igv_type = '1'  # Inafecto - Operación Onerosa
        if len(isc) >= 1:
            self.isc_type = '1'


class AccountInvoiceRefund(models.TransientModel):
    """Credit Notes"""
    _inherit = "account.invoice.refund"

    # @api.multi
    # def invoice_refund(self):
    #     res = super(AccountInvoiceRefund, self).invoice_refund()
    #     if self.filter_refund == 'cancel':
    #         _logger.info("Anulación")
    #         config = _get_config(self)
    #         if config.electronic_invoicing:
    #             inv_obj = self.env['account.invoice']
    #             context = dict(self._context or {})
    #             if res:
    #                 for inv in inv_obj.browse(context.get('active_ids')):
    #                     inv.anular_sunat(self.description, config)
    #     return res
