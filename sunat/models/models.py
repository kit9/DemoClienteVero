# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class EinvoiceCatalogTmpl(models.Model):
    _name = 'einvoice.catalog.tmpl'
    _description = 'Catalog Template'

    code = fields.Char(string='Code', size=4, index=True, required=True)
    name = fields.Char(string='Description', size=128, index=True, required=True)

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result


class EinvoiceCatalog09(models.Model):
    _name = "einvoice.catalog.09"
    _description = 'Codigos de Tipo de Nota de Credito Electronica'
    _inherit = 'einvoice.catalog.tmpl'


class NubefactOperationType(models.Model):
    _name = "nubefact.operation_type"
    _description = 'Codigos de Tipo de Operacion Nubefact'
    _inherit = 'einvoice.catalog.tmpl'


# 0003 - Incio
class Series(models.Model):
    _name = 'sunat.series'
    _description = "Series"
    _sql_constraints = [
        ('name_unique', 'unique(name)', "You cannot duplicate value in the Series field!")
    ]

    name = fields.Char(string="Serie", required=True)
    sequence_id = fields.Many2one('ir.sequence', string='Sequence',
                                  help="This field contains information on the numbering of electronic invoicing.",
                                  ondelete="cascade", readonly=True, copy=False)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.sequence_id:
                rec.sequence_id.unlink()
            res = super(Series, rec).unlink()
        return res

    @api.model
    def create(self, vals):
        res = super(Series, self).create(vals)
        if res:
            res.create_sequence()
        return res

    @api.multi
    def create_sequence(self):
        for rec in self:
            if not rec.sequence_id:
                seq = {
                    'name': 'Secuencia ' + str(rec.name),
                    'implementation': 'no_gap',
                    'code': 'sunat.invoice',
                    'padding': 9,
                }
                seq = self.env['ir.sequence'].create(seq)
                if seq:
                    rec.sequence_id = seq and seq.id or False


class ProductoSunat(models.Model):
    _name = "sunat.product"
    _description = 'Codigos de Productos Sunat'
    _inherit = 'einvoice.catalog.tmpl'

    code = fields.Char(string='Code', size=8, index=True, required=True)
    # 0003 - Fin


class detracciones(models.Model):
    _name = 'sunat.detracciones'
    _description = "Codigos de Detracciones"

    # name = fields.Text(string="Description", translate=True)
    name = fields.Text(string="Description", compute="_detracciones_full", store=True, copy=False)
    description = fields.Text(string="Descripción", translate=True)
    detrac = fields.Float(string="Detraction", digits=(16, 4))
    number = fields.Char(string="Número", size=3, index=True)
    detracmack = fields.Char(string="percentage", compute="_obtener_detraccion", translate=True)
    nubefact_id = fields.Char(string="Id Nubefact", size=3, index=True)

    def _obtener_detraccion(self):
        for rec in self:
            detrac = str(rec.detrac)
            rec.detracmack = "{}%".format(detrac)

    @api.depends('number', 'description')
    @api.multi
    def _detracciones_full(self):
        for rec in self:
            if rec.description == 'No Aplica':
                rec.name = rec.description
            else:
                rec.name = "%s %s" % (rec.number or '', rec.description or '')


class document_type(models.Model):
    _name = 'sunat.document_type'
    _description = "Tipos de Documentos"

    name = fields.Text(compute="_document_type_full", store=True, copy=False)
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

    name = fields.Text(compute="_document_type_identity_full", store=True, copy=False)
    number = fields.Char(string="Número", size=2, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    @api.depends('number', 'description')
    @api.multi
    def _document_type_identity_full(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class customs_code(models.Model):
    _name = 'sunat.customs_code'
    _description = "Codigos de Aduana"

    name = fields.Text(compute="_customs_code_full", store=True, copy=False)
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

    name = fields.Text(compute="_classification_goods_full", store=True, copy=False)
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

    name = fields.Text(compute="_Stock_Catalog", store=True, copy=False)
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

    name = fields.Text(compute="_Type_Existence", store=True, copy=False)
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

    name = fields.Text(compute="_Type_Operation", store=True, copy=False)
    number = fields.Char(string="Número", size=2, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    @api.depends('number', 'description')
    @api.multi
    def _Type_Operation(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class TypeIncome(models.Model):
    _name = 'sunat.type_income'
    _description = "Tipo de Renta"

    name = fields.Text(compute="_Type_Income", store=True, copy=False)
    number = fields.Char(string="Número", size=2, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    @api.depends('number', 'description')
    @api.multi
    def _Type_Income(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class TypeOperationDetraction(models.Model):
    _name = 'sunat.type_operation_detraction'
    _description = "Tipo de Operación de Detracción"

    name = fields.Text(compute="_Type_Operation", store=True, copy=False)
    number = fields.Char(string="Número", size=2, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    @api.depends('number', 'description')
    @api.multi
    def _Type_Operation(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class CodeGoods(models.Model):
    _name = 'sunat.code_goods'
    _description = "Codigo de Bienes"

    name = fields.Text(compute="_code_goods", store=True, copy=False)
    number = fields.Char(string="Número", size=3, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    @api.depends('number', 'description')
    @api.multi
    def _code_goods(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


class PaymentMethods(models.Model):
    _name = 'sunat.payment_methods'
    _description = "Metodos de Pago"

    name = fields.Text(compute="_payment_methods", store=True, copy=False)
    number = fields.Char(string="Número", size=3, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    @api.depends('number', 'description')
    @api.multi
    def _payment_methods(self):
        for rec in self:
            if len(rec.description) < 51:
                rec.name = "%s %s" % (rec.number or '', rec.description or '')
            else:
                rec.name = "%s %s..." % (rec.number or '', rec.description[:50] or '')


class Perception(models.Model):
    _name = 'sunat.perception'
    _description = "Porcentaje de Percepción"

    name = fields.Text(compute="_perception", store=True, copy=False)
    number = fields.Char(string="Número", size=3, translate=True, index=True)
    percentage = fields.Float(string="Porcentaje", translate=True)
    description = fields.Text(string="Descripción", translate=True)

    @api.depends('number', 'description')
    @api.multi
    def _perception(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')


# 0011
class SunatLegalPersons(models.Model):
    _name = "sunat.legal_persons"
    _description = "Sunat Personas Jurídicas"
    _sql_constraints = [
        ('name_unique', 'unique(name)', "You cannot duplicate value in the Ruc field!")
    ]

    name = fields.Char(string='Ruc', size=12, index=True, required=True)
    business_name = fields.Char(string='Business Name')
    date = fields.Date(string="From")
    resolution = fields.Char(string="Resolution")
    good_contributor = fields.Boolean(string="Good Contributor", index=True)
    retention_agent = fields.Boolean(string="Retention Agent", index=True)
    perception_agent = fields.Boolean(string="Perception Agent", index=True)
    # 0011


class AnyHistory(models.Model):
    _name = "sunat.any_history"
    _description = "Historial de Cualquier Proceso"

    date = fields.Datetime(string="Date Time")
    description = fields.Char(string="Description")
    content = fields.Text(string="Content")
    type = fields.Char(string="Type")
