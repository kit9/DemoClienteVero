# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    destination = fields.Boolean(string='Tiene Cuenta Destino', default=False)

    target_debit_id = fields.Many2one('account.account', string='Cuenta Debe')
    target_credit_id = fields.Many2one('account.account', string='Cuenta Haber')


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    move_analytic_id = fields.Many2one('account.move', string='Analytical Seat', translate=True)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def account_analytic_destino(self):
        accounts = []
        if self.state == "posted":
            for account in self.line_ids:
                if account.analytic_account_id.destination:
                    accounts.append(account)

        if len(accounts) > 0:
            for account in accounts:
                # Lista de Lineas
                lines = []

                # monto
                monto = 0
                if account.debit:
                    monto = account.debit
                else:
                    if account.credit:
                        monto = account.credit

                # Linea 2
                lines.append((0, 0, {
                    'account_id': account.analytic_account_id.target_credit_id and account.analytic_account_id.target_credit_id.id or False,
                    'credit': monto
                }))

                # Linea 1
                lines.append((0, 0, {
                    'account_id': account.analytic_account_id.target_debit_id and account.analytic_account_id.target_debit_id.id or False,
                    'debit': monto
                }))

                # Asiento
                account_move_dic = {
                    'date': str(datetime.now().date()) or False,
                    'journal_id': self.journal_id and self.journal_id.id or False,
                    'ref': self.ref,
                    'line_ids': lines
                }

                account_move = self.env['account.move'].create(account_move_dic)
                account_move.post()

                account.move_analytic_id = account_move and account_move.id or False
