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
    number = fields.Char(string="Number", size=2, translate=True)
    description = fields.Text(string="Description", translate=True)

    def _document_type_full(self):
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
    #Experimentos
    file_txt = fields.Binary(compute="_generate_txt")
    file_demo = fields.Binary(string="Archivo")
    file_name = fields.Char(compute="_generate_name_txt")

    def _generate_txt(self):
        content = '-'
        for rec in self:
            content = "%s%s" % (rec.detraccion or '-', rec.detrac_id.detrac or '-')
            rec.file_txt = base64.encodestring(content.encode('ISO-8859-1'))
    
    def _generate_name_txt(self):
        for rec in self:
            rec.file_name = 'txt_file.txt'

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
