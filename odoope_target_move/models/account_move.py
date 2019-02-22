# -*- coding: utf-8 -*-

import time
from collections import OrderedDict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
from lxml import etree

import logging

_logger = logging.getLogger(__name__)


# ----------------------------------------------------------
# Entries
# ----------------------------------------------------------


class AccountMove(models.Model):
    _inherit = "account.move"

    target = fields.Boolean(string='Destino Procesado', default=False)

    @api.multi
    def post(self):

        for move in self:
            # Aqui empieza
            account_ids = []  # acumulador de cuentas
            account = self.env['account.account']
            account_move = self.env['account.move.line']
            # verifica si existen lineas
            if len(move.line_ids) > 0:
                # Valida si ya fue ejecutado el amarre en el asiento
                if move.target == False:
                    for l in move.line_ids:
                        account_id = l.account_id.id
                        if account_id in account_ids:  # Para evitar Bucles
                            continue
                        if account.browse(account_id).target_account == True:
                            # Duplica las lineas y las guarda en las variables debe y haber con valores predefinidos, se anulan los campos de "tax" para evitar que se dupliquen los impuestos en el arbol de declaracion de impuestos
                            debit = l.copy({'tax_ids': False})
                            _logger.debug(debit)
                            credit = l.copy({'tax_ids': False})
                            _logger.debug(credit)
                            if l.debit != False:
                                debit.write({
                                    'account_id': account.browse(l.account_id.id).target_debit_id.id,
                                    'debit': l.debit,
                                    'credit': False,
                                    'amount_currency': l.amount_currency,
                                })
                                credit.write({
                                    'account_id': account.browse(l.account_id.id).target_credit_id.id,
                                    'debit': False,
                                    'credit': l.debit,
                                    'amount_currency': l.amount_currency * -1.0,
                                })
                            else:
                                debit.write({
                                    'account_id': account_obj.browse(l.account_id.id).target_debit_id.id,
                                    'debit': False,
                                    'credit': l.credit,
                                    'amount_currency': l.amount_currency,
                                })
                                credit.write({
                                    'account_id': account_obj.browse(l.account_id.id).target_credit_id.id,
                                    'debit': l.credit,
                                    'credit': False,
                                    'amount_currency': l.amount_currency * -1.0,
                                })
                    account_ids.append(account_id)  # acumulando cuentas
                move.target = True
                # Aqui termina la modificacion
        res = super(AccountMove, self).post()

        return True
