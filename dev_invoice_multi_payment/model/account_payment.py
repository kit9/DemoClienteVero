# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class account_payment(models.Model):
    _inherit = 'account.payment'

    payment_for = fields.Selection([('multi_payment', 'AP Payment')], string='Payment Method')
    line_ids = fields.One2many('advance.payment.line', 'account_payment_id')
    full_reco = fields.Boolean('Full Reconcile')
    invoice_ids = fields.Many2many('account.invoice', 'account_invoice_payment_rel', 'payment_id', 'invoice_id',
                                   string="Invoices", copy=False, readonly=False)

    number_payment = fields.Integer(string="Numero de Pago Masivo")
    type = fields.Selection([('detraccion', 'Detracción'), ('retencion', 'Retención'), ('factura', 'Factura')],
                            string='Tipo de Pago')

    @api.multi
    @api.depends('back_partner_id')
    def _get_banco(self):
        for rec in self:
            if rec.back_partner_id:
                rec.vv_bank = rec.back_partner_id.bank_id.name + " " + rec.back_partner_id.acc_number or ""

    @api.multi
    @api.onchange('payment_for')
    def onchange_payment_for(self):
        if self.payment_for == 'multi_payment':
            self.onchange_partner_id()
        elif self.payment_for != 'multi_payment':
            if self.line_ids:
                for line in self.line_ids:
                    line.account_payment_id = False
            if self.invoice_ids:
                self.invoice_ids = False

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.payment_for == 'multi_payment':
            acc_invoice = []
            account_inv_obj = self.env['account.invoice']
            invoice_ids = []
            if self.partner_type == 'customer':
                invoice_ids = account_inv_obj.search(
                    [('partner_id', 'in', [self.partner_id.id]), ('state', '=', 'open'),
                     ('type', 'in', ['out_invoice', 'out_refund']), ('company_id', '=', self.company_id.id)])
            else:
                invoice_ids = account_inv_obj.search(
                    [('partner_id', 'in', [self.partner_id.id]), ('state', '=', 'open'),
                     ('type', 'in', ['in_invoice', 'in_refund']), ('company_id', '=', self.company_id.id)])
            curr_pool = self.env['res.currency']
            for vals in invoice_ids:
                original_amount = vals.amount_total
                balance_amount = vals.residual
                allocation = vals.residual
                if vals.currency_id.id != self.currency_id.id:
                    original_amount = vals.amount_total
                    balance_amount = vals.residual
                    allocation = vals.residual
                    if vals.currency_id.id != self.currency_id.id:
                        currency_id = self.currency_id.with_context(date=self.payment_date)
                        original_amount = curr_pool._compute(vals.currency_id, currency_id, original_amount, round=True)
                        balance_amount = curr_pool._compute(vals.currency_id, currency_id, balance_amount, round=True)
                        allocation = curr_pool._compute(vals.currency_id, currency_id, allocation, round=True)

                acc_invoice.append({'invoice_id': vals.id, 'account_id': vals.account_id.id,
                                    'date': vals.date_invoice, 'due_date': vals.date_due,
                                    'original_amount': original_amount, 'balance_amount': balance_amount,
                                    'allocation': 0.0, 'full_reconclle': False, 'currency_id': self.currency_id.id})
            self.line_ids = acc_invoice
            self.invoice_ids = [(6, 0, invoice_ids.ids)]

    @api.onchange('currency_id')
    def onchange_currency(self):
        curr_pool = self.env['res.currency']
        if self.currency_id and self.line_ids:
            for line in self.line_ids:
                if line.currency_id.id != self.currency_id.id:
                    currency_id = self.currency_id.with_context(date=self.payment_date)
                    line.original_amount = curr_pool._compute(line.currency_id, currency_id, line.original_amount,
                                                              round=True)
                    line.balance_amount = curr_pool._compute(line.currency_id, currency_id, line.balance_amount,
                                                             round=True)
                    line.allocation = curr_pool._compute(line.currency_id, currency_id, line.allocation, round=True)
                    line.currency_id = self.currency_id and self.currency_id.id or False

    @api.multi
    def post(self):
        if self.line_ids and self.payment_for == 'multi_payment':
            amt = 0.0
            invoice_ids = []
            for line in self.line_ids:
                invoice_ids.append(line.invoice_id.id)
                amt += line.allocation
            if self.amount < amt:
                raise ValidationError(("Amount is must be greater or equal '%s'") % (amt))
            if self.amount > amt:
                self.full_reco = True
            self.invoice_ids = [(6, 0, invoice_ids)]
        return super(account_payment, self).post()

    @api.multi
    def get_inv_pay_amount(self, inv):
        amt = 0
        if self.partner_type == 'customer':
            for line in self.line_ids:
                if line.invoice_id.id == inv.id:
                    if inv.type == 'out_invoice':
                        amt = -(line.allocation)
                    else:
                        amt = line.allocation
        else:
            for line in self.line_ids:
                if line.invoice_id.id == inv.id:
                    if inv.type == 'in_invoice':
                        amt = line.allocation
                    else:
                        amt = -(line.allocation)
        return amt

    @api.multi
    def _create_multi_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment
            references invoice(s) they are reconciled.
            Return the journal entry.
        """
        aml_obj = self.env['account.move.line']. \
            with_context(check_move_validity=False)
        invoice_currency = False
        if self.invoice_ids and \
                all([x.currency_id == self.invoice_ids[0].currency_id
                     for x in self.invoice_ids]):
            # If all the invoices selected share the same currency,
            # record the paiement in that currency too
            invoice_currency = self.invoice_ids[0].currency_id
        move = self.env['account.move'].create(self._get_move_vals())
        p_id = str(self.partner_id.id)
        pay_amt = 0
        for inv in self.invoice_ids:
            amt = self.get_inv_pay_amount(inv)
            if amt:
                pay_amt += amt
                debit, credit, amount_currency, currency_id = \
                    aml_obj.with_context(date=self.payment_date). \
                        _compute_amount_fields(amt, self.currency_id,
                                               self.company_id.currency_id)
                # Write line corresponding to invoice payment
                counterpart_aml_dict = \
                    self._get_shared_move_line_vals(debit,
                                                    credit, amount_currency,
                                                    move.id, False)
                counterpart_aml_dict.update(
                    self._get_counterpart_move_line_vals(inv))
                counterpart_aml_dict.update({'currency_id': currency_id})
                counterpart_aml = aml_obj.create(counterpart_aml_dict)
                # Reconcile with the invoices and write off
                inv.register_payment(counterpart_aml)

                # Write counterpart lines
                if not self.currency_id != self.company_id.currency_id:
                    amount_currency = 0
                liquidity_aml_dict = \
                    self._get_shared_move_line_vals(credit, debit,
                                                    -amount_currency, move.id,
                                                    False)
                liquidity_aml_dict.update(
                    self._get_liquidity_move_line_vals(-amount))
                aml_obj.create(liquidity_aml_dict)

        if self.full_reco:
            o_amt = amount - pay_amt
            debit, credit, amount_currency, currency_id = \
                aml_obj.with_context(date=self.payment_date). \
                    _compute_amount_fields(o_amt, self.currency_id,
                                           self.company_id.currency_id)
            # Write line corresponding to invoice payment
            counterpart_aml_dict = \
                self._get_shared_move_line_vals(debit,
                                                credit, amount_currency,
                                                move.id, False)
            counterpart_aml_dict.update(
                self._get_counterpart_move_line_vals(False))
            counterpart_aml_dict.update({'currency_id': currency_id})
            counterpart_aml = aml_obj.create(counterpart_aml_dict)
            # Reconcile with the invoices and write off
            #                inv.register_payment(counterpart_aml)

            # Write counterpart lines
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0
            liquidity_aml_dict = \
                self._get_shared_move_line_vals(credit, debit,
                                                -amount_currency, move.id,
                                                False)
            liquidity_aml_dict.update(
                self._get_liquidity_move_line_vals(-amount))
            aml_obj.create(liquidity_aml_dict)
        move.post()
        return move

    @api.multi
    def _create_payment_entry(self, amount):
        if self.invoice_ids and self.line_ids and self.payment_for == 'multi_payment':
            moves = self._create_multi_payment_entry(amount)
            return moves
        return super(account_payment, self)._create_payment_entry(amount)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
