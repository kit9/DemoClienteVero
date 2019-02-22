# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import logging

_logger = logging.getLogger(__name__)


class purchase_order(models.Model):
    _inherit = 'sale.order'

    waiting_orders = fields.Char(string="Pedidos de Espera", compute="_compute_waiting_orders")

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
