# -*- coding: utf-8 -*-

from odoo import models, fields, api


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

    name = fields.Text(string="Description", translate=True)
    number = fields.Char(string="Number",size=2, translate=True)


class account_invoice(models.Model):
    _inherit = "account.invoice"

    # Detraction
    detrac_id = fields.Many2one('sunat.detracciones', 'Detraccion')
    # Value of the Detraction
    detraccion = fields.Monetary(
        string="Detraccion", compute="_calcular_detrac", store=True)
    # Document Type
    document_type_id = fields.Many2one('sunat.document_type', 'Document Type')
    # Apply Retention
    apply_retention = fields.Boolean(string="Apply Retention")
    # Hide or not Apply Retention
    hide_apply_retention = fields.Boolean(
        string='Hide', compute="_compute_hide_apply_retention")
    detraccion_paid = fields.Boolean()

    # Method to hide Apply Retention
    @api.depends('document_type_id')
    def _compute_hide_apply_retention(self):
        if self.document_type_id.number == '02':
            self.hide_apply_retention = False
        else:
            self.hide_apply_retention = True

    # Load the retention of the selected provider
    @api.onchange('partner_id')
    def _onchange_proveedor(self):
        #if len(self.detrac_id) <= 0 :
        self.detrac_id = self.partner_id.detrac_id

    # Calculate the value of the Detraction
    @api.depends('amount_total', 'detrac_id')
    @api.multi
    def _calcular_detrac(self):
        for record in self:
            record.detraccion = record.amount_total * \
                (record.detrac_id.detrac / 100)
    
    # Trial Action
    @api.multi
    def action_prueba(self):
        for rec in self:
            rec.reference = 'FacturaDePrueba'
        return True

    # Action Paid Detraccion
    @api.multi
    def action_paid_detraccion(self):
        for rec in self:
            rec.detraccion_paid = True
        return True
