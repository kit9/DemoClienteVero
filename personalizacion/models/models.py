# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import logging

_logger = logging.getLogger(__name__)


class purchase_order(models.Model):
    _inherit = 'sale.order'

    waiting_orders = fields.Char(
        string="Pedidos de Espera", compute="_compute_waiting_orders")

    @api.multi
    def _compute_waiting_orders(self):
        for rec in self:
            detector = "NO"
            for line in rec.order_line:
                if line.product_uom_qty > line.qty_delivered:
                    detector = "SI"
            # contador = 0
            # for ob in rec.picking_ids:
            #     if ob.state == "assigned":
            #         contador = contador + 1
            # rec.waiting_orders = "%s" % (contador)
            rec.waiting_orders = detector


class fabricacion(models.Model):
    _inherit = 'mrp.production'

    expected_duration = fields.Float(
        string="Duración Esperada", compute="_expected_duration")
    real_duration = fields.Char(
        string="Duración Real", compute="_real_duration")

    @api.multi
    def _expected_duration(self):
        for rec in self:
            if len(rec.workorder_ids) > 0:
                worck = rec.workorder_ids[0]
                rec.expected_duration = worck.duration_expected

    @api.multi
    def _real_duration(self):
        for rec in self:
            if len(rec.workorder_ids) > 0:
                worck = rec.workorder_ids[0]
                rec.real_duration = str(worck.duration)
