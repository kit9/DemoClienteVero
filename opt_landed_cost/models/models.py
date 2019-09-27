# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    def get_valuation_lines(self):
        lines = []
        for move in self.mapped('picking_ids').mapped('move_lines'):
            # it doesn't make sense to make a landed cost for a product that isn't set as being valuated in real time at real cost
            if move.product_id.valuation != 'real_time' or move.product_id.cost_method not in 'fifo,average':
                continue
            vals = {
                'product_id': move.product_id.id,
                'move_id': move.id,
                'quantity': move.product_qty,
                'former_cost': move.value,
                'weight': move.product_id.weight * move.product_qty,
                'volume': move.product_id.volume * move.product_qty
            }
            lines.append(vals)

        if not lines and self.mapped('picking_ids'):
            raise UserError(_(
                "You cannot apply landed costs on the chosen transfer(s). Landed costs can only be applied for products with automated inventory valuation and FIFO costing method."))
        return lines


class LandedCost(models.Model):
    _inherit = "stock.landed.cost"

    @api.multi
    def _calculated_cost(self):
        for rec in self:
            if rec.state == 'done':
                rec.valuation_adjustment_lines._calculated_cost()


class AdjustmentLines(models.Model):
    _inherit = "stock.valuation.adjustment.lines"

    calculated_cost = fields.Boolean(string='Costo Calculado', default=False)

    @api.multi
    def _calculated_cost(self):
        for rec in self:
            if not rec.calculated_cost:
                account_id = rec.product_id.property_account_expense_id or \
                             rec.product_id.categ_id.property_account_expense_categ_id
                if not account_id:
                    account_id = self.env['account.account'].search([], limit=1)
                total = rec.product_id.qty_available * rec.product_id.standard_price
                total = total + rec.additional_landed_cost
                total = total / rec.product_id.qty_available
                rec.product_id.do_change_standard_price(total, account_id.id)
                rec.calculated_cost = True

# class StockLandedCostRegistry(models.Model):
#     _name = "stock.landed.cost.registry"
#     _description = "Registro de los movimientos de Gastos de Envío"
#
#     name = fields.Char(string="Nombre")
#     product_id = fields.Many2one('product.product', string='Product')
#
#
# class StockMoveLine(models.Model):
#     _inherit = "stock.move.line"
#
#     registry_id = fields.Many2one(comodel_name='stock.landed.cost.registry', string='Registry')
#
#
# class StockLandedCostRegistry(models.Model):
#     _inherit = "stock.landed.cost.registry"
#
#     registry_id = fields
#
#     @api.model
#     def create_registry(self, product):
#         stock_move_line_obj = self.env['stock.move.line']
#         if product:
#             domain = [
#                 ('state', 'like', 'done'),
#                 ('product_id', '=', product.id)
#             ]
#             stock_move_line = stock_move_line_obj.search(domain)
