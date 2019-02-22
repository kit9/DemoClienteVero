# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time
import logging

_logger = logging.getLogger(__name__)


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    waiting_orders = fields.Char(string="Pedidos de Espera", compute="_compute_waiting_orders")
    billing = fields.Char(string="Facturación", compute="_compute_billing")
    seat_generated = fields.Boolean(string="Recepciones no Facturadas", copy=False)

    @api.multi
    def _compute_waiting_orders(self):
        for rec in self:
            contador = 0
            for ob in rec.picking_ids:
                if ob.state == "assigned":
                    contador = contador + 1
            rec.waiting_orders = "%s" % (contador)

    @api.multi
    def _compute_billing(self):
        for rec in self:
            if rec.state == "purchase":
                nofacturado = 0
                facturado = 0
                recibido = 0
                for lines in rec.order_line:
                    recibido = recibido + lines.qty_received
                    cantidad = lines.qty_received - lines.qty_invoiced
                    if cantidad == 0:
                        facturado = facturado + 1
                    else:
                        if cantidad == lines.qty_received:
                            nofacturado = nofacturado + 1
                        else:
                            nofacturado = nofacturado + 1
                            facturado = facturado + 1
                            rec.billing = "Parcial"
                            break
                if recibido == 0:
                    # rec.billing = "-"
                    rec.billing = "No"
                else:
                    if facturado > 0 and nofacturado == 0:
                        rec.billing = "Si"
                    else:
                        if nofacturado > 0 and facturado == 0:
                            rec.billing = "No"
                        else:
                            if nofacturado > 0 and facturado > 0:
                                rec.billing = "Parcial"
                            else:
                                rec.billing = "--"

            else:
                rec.billing = "--"
                # rec.billing = "No"

    # Trial Action
    @api.multi
    def receptions_not_invoiced(self):
        for rec in self:

            if (rec.billing == "Parcial" or rec.billing == "No") and rec.seat_generated == False:
                # Diario Contable
                journal = self.env['account.journal'].search([('name', 'like', 'Vendor Bills')], limit=1)
                if not journal:
                    journal = self.env['account.journal'].search([], limit=1)

                # Diario Contable 1 y 2
                account1 = self.env['account.account'].search([('code', 'like', '60101')], limit=1)
                if not account1:
                    account1 = self.env['account.account'].search([], limit=1)
                account2 = self.env['account.account'].search([('code', 'like', '4211')], limit=1)
                if not account2:
                    account2 = self.env['account.account'].search([], limit=1)

                # Campo
                referencia = ""

                # Monto Monetario
                cantidad = 0
                for line in rec.order_line:
                    numero = line.qty_received - line.qty_invoiced
                    cantidad = cantidad + (numero * line.price_unit)
                    for item in line.move_ids:
                        referencia = referencia + item.reference + ","

                referencia = referencia[0:len(referencia) - 1] or ""

                cantidad = round(cantidad, 2)

                # Lista de Lineas
                lines = []

                # Linea 2 - 4211
                lines.append((0, 0, {
                    'account_id': account2 and account2.id or False,
                    'credit': cantidad
                }))

                # Linea 1 - 60101
                lines.append((0, 0, {
                    'account_id': account1 and account1.id or False,
                    'debit': cantidad
                }))

                # Asiento
                account_move_dic = {
                    'date': time.strftime("%Y-%m-%d"),
                    'journal_id': journal and journal.id or False,
                    'ref': referencia,
                    'line_ids': lines
                }

                account_move = self.env['account.move'].create(account_move_dic)

                account_move.post()
                rec.seat_generated = True

        return True
