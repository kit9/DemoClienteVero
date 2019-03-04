# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class stock_move_line(models.Model):
    _inherit = 'stock.move.line'

    unit_price = fields.Float(string="Unitario", compute="_unit_price")
    quantity = fields.Float(string="Cantidad", compute="_quantity", store=True)
    total_price = fields.Float(string="Total", compute="_total_price", store=True)

    # Para filtrar
    month_year_inv = fields.Char(compute="_get_month_invoice", store=True, copy=False)

    # Datos Historicos
    balance_quantity = fields.Integer(string="Cantidad Historico")
    historical_cost = fields.Float(string="Costo Historico")

    @api.multi
    @api.depends('date')
    def _get_month_invoice(self):
        for rec in self:
            if rec.date:
                rec.month_year_inv = rec.date.strftime("%m%Y")

    @api.multi
    @api.depends('product_id', 'qty_done', 'reference', 'move_id')
    def _unit_price(self):
        for rec in self:
            if rec.move_id.purchase_line_id:
                rec.unit_price = rec.move_id.purchase_line_id.price_unit
            else:
                if rec.move_id.sale_line_id:
                    rec.unit_price = rec.historical_cost
                else:
                    rec.unit_price = rec.product_id.standard_price

    @api.multi
    @api.depends('reference', 'qty_done')
    def _quantity(self):
        for rec in self:
            if "OUT" in rec.reference:
                rec.quantity = (rec.qty_done * -1)
            else:
                rec.quantity = rec.qty_done

    @api.multi
    @api.depends('product_id', 'qty_done', 'reference', 'move_id')
    def _total_price(self):
        for rec in self:
            # Stock Move
            if rec.move_id.purchase_line_id:
                rec.total_price = rec.move_id.purchase_line_id.price_unit * rec.qty_done
            else:
                if rec.move_id.sale_line_id:
                    rec.total_price = rec.historical_cost * rec.qty_done
                else:
                    rec.total_price = rec.product_id.standard_price * rec.qty_done
            if "OUT" in rec.reference:
                rec.total_price = rec.total_price * -1
