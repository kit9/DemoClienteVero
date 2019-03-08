# -*- coding: utf-8 -*-

from odoo import models, fields, api
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


class TypeIncome(models.Model):
    _name = 'sunat.type_income'
    _description = "Tipo de Renta"

    name = fields.Text(compute="_Type_Income", store=True)
    number = fields.Char(string="Número", size=2, translate=True, index=True)
    description = fields.Text(string="Descripción", translate=True)

    @api.depends('number', 'description')
    @api.multi
    def _Type_Income(self):
        for rec in self:
            rec.name = "%s %s" % (rec.number or '', rec.description or '')
