from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     historical_cost = fields.Float("Costo Historico")
#
#
# class PurchaseOrderLine(models.Model):
#     _inherit = "purchase.order.line"
#
#     historical_cost = fields.Float("Costo Historico")
#
#
# class SaleOrder(models.Model):
#     _inherit = "sale.order"
#
#     @api.multi
#     def action_confirm(self):
#         res = super(SaleOrder, self).action_confirm()
#         for so in self:
#             for line in so.order_line:
#                 line.historical_cost = line.product_id.standard_price
#         return res
#
#
# class PurchaseOrder(models.Model):
#     _inherit = "purchase.order"
#
#     @api.multi
#     def button_confirm(self):
#         res = super(PurchaseOrder, self).button_confirm()
#         for po in self:
#             for line in po.order_line:
#                 line.historical_cost = line.product_id.standard_price
#         return res
