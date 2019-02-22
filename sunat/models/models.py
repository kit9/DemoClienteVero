# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class detracciones(models.Model):
    _name = 'sunat.detracciones'
    _description = "Codigos de Detracciones"

    name = fields.Text(string="Description", translate=True)
    detrac = fields.Integer(string="Detraction", translate=True)
    detracmack = fields.Char(string="percentage", compute="_obtener_detraccion", translate=True)

    def _obtener_detraccion(self):
        for rec in self:
            detrac = str(rec.detrac)
            rec.detracmack = "{}%".format(detrac)


class document_type(models.Model):
    _name = 'sunat.document_type'
    _description = "Tipos de Documentos"

    name = fields.Text(compute="_document_type_full", store=True)
    number = fields.Char(string="Número", size=2, translate=True, index=True)
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
    number = fields.Char(string="Número", size=2, translate=True, index=True)
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
    number = fields.Char(string="Número", size=2, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    def _currency_type_full(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class customs_code(models.Model):
    _name = 'sunat.customs_code'
    _description = "Codigos de Aduana"

    name = fields.Text(compute="_customs_code_full", store=True)
    number = fields.Char(string="Número", size=3, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    @api.depends('number', 'description')
    @api.multi
    def _customs_code_full(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class classification_goods(models.Model):
    _name = 'sunat.classification_goods'
    _description = "Clasificación de Bienes"

    name = fields.Text(compute="_classification_goods_full", store=True)
    number = fields.Char(string="Número", size=3, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    @api.depends('number', 'description')
    @api.multi
    def _classification_goods_full(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class StockCatalog(models.Model):
    _name = 'sunat.stock_catalog'
    _description = "Catálogo de Stock"

    name = fields.Text(compute="_Stock_Catalog", store=True)
    number = fields.Char(string="Número", size=2, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    @api.depends('number', 'description')
    @api.multi
    def _Stock_Catalog(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class TypeExistence(models.Model):
    _name = 'sunat.type_existence'
    _description = "Tipo de Existencia"

    name = fields.Text(compute="_Type_Existence", store=True)
    number = fields.Char(string="Número", size=2, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    @api.depends('number', 'description')
    @api.multi
    def _Type_Existence(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class TypeOperation(models.Model):
    _name = 'sunat.type_operation'
    _description = "Tipo de Operación"

    name = fields.Text(compute="_Type_Operation", store=True)
    number = fields.Char(string="Número", size=2, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    @api.depends('number', 'description')
    @api.multi
    def _Type_Operation(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    catalog_id = fields.Many2one('sunat.stock_catalog', 'Catálogo de Stock')
    type_existence_id = fields.Many2one('sunat.type_existence', 'Tipo de Existencia')
    existence_code = fields.Char(string="Código de Existencia")


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    type_operation_id = fields.Many2one('sunat.type_operation', 'Tipo de Operación')
    document_type_id = fields.Many2one('sunat.document_type', 'Document Type')


class UoM(models.Model):
    _inherit = 'uom.uom'

    sunat_code = fields.Char(string="Código de Sunat", default="99")


class AccountAccount(models.Model):
    _inherit = "account.account"

    target_debit1_id = fields.Many2one('account.account', string='Cuenta de amarre al Debe 1')
    target_debit1_value = fields.Integer(string="Porcentaje 1")

    target_debit2_id = fields.Many2one('account.account', string='Cuenta de amarre al Debe 2')
    target_debit2_value = fields.Integer(string="Porcentaje 2")

    target_debit3_id = fields.Many2one('account.account', string='Cuenta de amarre al Debe 3')
    target_debit3_value = fields.Integer(string="Porcentaje 3")

    target_credit_id = fields.Many2one('account.account', string='Cuenta de amarre al Haber')
    target_account = fields.Boolean(string='Tiene cuenta destino', default=False)

    def imprimir(self):
        _logger.info("Crear asiento")


class account_move(models.Model):
    _inherit = 'account.move'

    def asiento_destino(self):
        accounts = []
        if self.state == "posted":
            for account in self.line_ids:
                if account.account_id.target_account:
                    accounts.append(account)
        if len(accounts) > 0:
            # Lista de Lineas
            lines = []

            for account in accounts:
                # monto
                monto = 0
                if account.debit:
                    monto = account.debit;
                else:
                    if account.credit:
                        monto = account.credit;

                # Linea 4
                lines.append((0, 0, {
                    'account_id': account.account_id.target_credit_id and account.account_id.target_credit_id.id or False,
                    'credit': monto
                }))

                # Linea 3
                if account.account_id.target_debit3_id:
                    lines.append((0, 0, {
                        'account_id': account.account_id.target_debit3_id and account.account_id.target_debit3_id.id or False,
                        'debit': monto * (account.account_id.target_debit3_value / 100)
                    }))

                # Linea 2
                if account.account_id.target_debit2_id:
                    lines.append((0, 0, {
                        'account_id': account.account_id.target_debit2_id and account.account_id.target_debit2_id.id or False,
                        'debit': monto * (account.account_id.target_debit2_value / 100)
                    }))

                # Linea 1
                if account.account_id.target_debit1_id:
                    lines.append((0, 0, {
                        'account_id': account.account_id.target_debit1_id and account.account_id.target_debit1_id.id or False,
                        'debit': monto * (account.account_id.target_debit1_value / 100)
                    }))

            # Asiento
            account_move_dic = {
                'date': str(datetime.now().date()) or False,
                'journal_id': self.journal_id and self.journal_id.id or False,
                'ref': self.ref,
                'line_ids': lines
            }

            account_move = self.env['account.move'].create(account_move_dic)


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
    is_empresa = fields.Boolean(compute="_is_empresa")
    is_withholding_agent = fields.Boolean(string="Agente de Retención")

    # Datos Persona Natural
    ape_pat = fields.Char(string="Apellido Paterno")
    ape_mat = fields.Char(string="Apellido Materno")
    nombres = fields.Char(string="Nombre Completo")

    # Datos Persona Juridica
    age_retencion = fields.Boolean(string="Agente de Retención")
    buen_contribuyente = fields.Boolean(string="Buen Contribuyente")
    age_percepcion = fields.Boolean(string="Agente de Percepción")

    @api.multi
    @api.depends('person_type')
    def _is_empresa(self):
        for rec in self:
            if rec.person_type == '02-Persona Jurídica':
                rec.is_empresa = True
            else:
                rec.is_empresa = False
            # _logger.info("Variable -> " + str(rec.is_empresa))


class res_partner_bank(models.Model):
    _inherit = 'res.partner.bank'

    is_detraction = fields.Boolean(string="Detracción")
    is_retention = fields.Boolean(string="Retención")
    priority = fields.Integer(string="Prioridad")
