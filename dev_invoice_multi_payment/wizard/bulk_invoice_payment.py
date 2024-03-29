# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import itertools
from operator import itemgetter
import operator
import logging

_logger = logging.getLogger(__name__)


class bulk_invoice(models.TransientModel):
    _name = 'bulk.invoice'
    _description = "Facturas"

    invoice_id = fields.Many2one('account.invoice', string='Invoice')
    partner_id = fields.Many2one('res.partner', string='Partner')
    amount = fields.Float('Amount')
    paid_amount = fields.Float('Pay Amount')
    bulk_invoice_id = fields.Many2one('bulk.inv.payment')

    bulk_detraction_id = fields.Many2one('bulk.inv.detraction')

    bank_id = fields.Char(string='Banco', readonly=True)


class bulk_inv_payment(models.TransientModel):
    _name = 'bulk.inv.payment'
    _description = "Pago de Facturas"

    @api.model
    def default_get(self, fields):
        res = {}
        inv_ids = self._context.get('active_ids')
        vals = []
        invoice_ids = self.env['account.invoice'].browse(inv_ids)
        inv_type = ''
        for invo in invoice_ids:
            inv_type = invo.type
            break
        for inv in invoice_ids:
            if inv_type != inv.type:
                raise ValidationError('You must select only invoices or refunds.')
            if inv.state != 'open':
                raise ValidationError('Please Select Open Invoices.')
            vals.append((0, 0, {
                'invoice_id': inv and inv.id or False,
                'partner_id': inv and inv.partner_id.id or False,
                'amount': inv.residual or 0.0,
                'paid_amount': inv.residual or 0.0,
            }))
            if inv.type in ('out_invoice', 'out_refund'):
                res.update({
                    'partner_type': 'customer',
                })
            else:
                # 0001 - Incio - Movido
                # Inicio Codigo Optimiza
                if inv.detraccion_paid == False and inv.hide_detraction == False:
                    raise ValidationError('Debe pagar la detraccion de las facturas')
                # 0001 - Fin - Movido
                res.update({
                    'partner_type': 'supplier',
                })
        if inv_type in ('out_invoice', 'in_refund'):
            res.update({
                'payment_type': 'inbound'
            })
        else:
            res.update({
                'payment_type': 'outbound'
            })

        res.update({
            'invoice_ids': vals,
        })
        return res

    name = fields.Char('Name', default='hello')
    payment_type = fields.Selection([('outbound', 'Send Money'),
                                     ('inbound', 'Receive Money'),
                                     ('transfer', 'Transfer')],
                                    string="Payment Type", required="1")
    payment_date = fields.Date('Payment Date', required="1")
    communication = fields.Char('Memo')
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Supplier')], string='Partner Type')
    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))])
    invoice_ids = fields.One2many('bulk.invoice', 'bulk_invoice_id', string='Invoice')

    payment_methods_id = fields.Many2one('sunat.payment_methods', string='Forma de Pago')
    payment_methods_domain = fields.Char('Domain', compute="_payment_methods_domain")

    @api.multi
    def _payment_methods_domain(self):
        for rec in self:
            # total = sum(line.paid_amount for line in rec.invoice_ids)
            total = 10
            if total > 3501:
                rec.payment_methods_domain = "'003','007','009','011','012','013','014'"
            else:
                rec.payment_methods_domain = "'003','007'"

    @api.multi
    def process_payment(self):
        vals = []
        for line in self.invoice_ids:
            if line.paid_amount > 0.0:
                vals.append({
                    'invoice_id': line.invoice_id or False,
                    'partner_id': line.partner_id and line.partner_id.id or False,
                    'amount': line.amount or 0.0,
                    'paid_amount': line.paid_amount or 0.0,
                    'currency_id': line.invoice_id.currency_id.id or False,
                })
        new_vals = sorted(vals, key=itemgetter('partner_id'))
        groups = itertools.groupby(new_vals, key=operator.itemgetter('partner_id'))
        result = [{'partner_id': k, 'values': [x for x in v]} for k, v in groups]
        new_payment_ids = []
        # Iteraciones por proveedor
        for res in result:
            # Metodo de Pago
            payment_method_id = self.env['account.payment.method'].search([('name', 'like', 'Manual')], limit=1)
            if not payment_method_id:
                payment_method_id = self.env['account.payment.method'].search([], limit=1)

            retention_journal = self.env['account.journal'].search([('name', 'like', 'Retenciones')], limit=1)
            if not retention_journal:
                retention_journal = self.env['account.journal'].search([], limit=1)

            # Fecha de Pago
            payment_date = False
            if self.payment_date:
                payment_date = self.payment_date.strftime("%Y-%m-%d")

            # Validaciones de Retencion Proveedor
            apply_retention = True
            # 0001 - Incio
            is_detraction_client = True
            # 0001 - Fin
            total_payment = 0
            bank_retencion = False
            bank_factura = False
            proveedor_id = res.get('partner_id')
            proveedor = self.env['res.partner'].search([('id', 'like', proveedor_id)], limit=1)
            for inv_line in res.get('values'):
                invoice = inv_line.get('invoice_id')
                total_payment = total_payment + invoice.amount_total_signed

            # Condiciones que no permiten que se aplique la retención
            if proveedor.age_retencion:  # Si es agente de retencion no retiene
                apply_retention = False
            if total_payment < 700:
                # 0001 - Incio
                is_detraction_client = False
                # 0001 - Fin
                apply_retention = False

            # Obtenermos el banco para las retenciones
            for bank in proveedor.bank_ids:
                if bank.is_retention and not bank_retencion and not bank.is_detraction:
                    bank_retencion = bank
                if not bank.is_retention and not bank_factura and not bank.is_detraction:
                    bank_factura = bank

            # Iteraciones por Factura
            for inv_line in res.get('values'):

                # Factura
                inv_ids = []
                invoice = inv_line.get('invoice_id')
                inv_ids.append(invoice.id)

                if invoice.hide_detraction and apply_retention:
                    is_retencion = True
                    # 0001 - Incio
                    is_detraction_client = False
                    # 0001 - Fin
                else:
                    is_retencion = False
                    # 0001 - Incio
                    if not invoice.hide_detraction and is_detraction_client:
                        is_detraction_client = True
                    # 0001 - Fin

                # 0001 - Incio - Modificado
                if is_retencion and self.partner_type == "supplier":
                    tipo = "retencion"
                elif is_detraction_client and self.partner_type == "customer":
                    tipo = "detraccion"
                else:
                    tipo = "factura"
                # 0001 - Fin - Modificado

                Tipo_Pago = False
                if tipo == "retencion":
                    journal = retention_journal
                    banco = bank_retencion
                    moneda_venta = self.env['res.currency'].search([('name', 'like', 'PEN'), ('type', 'like', 'sale')],
                                                                   limit=1)
                    if moneda_venta:
                        currency = moneda_venta.id
                    else:
                        currency = res.get('values')[0].get('currency_id')
                # 0001 - Incio
                elif tipo == "detraccion":
                    banco = False
                    # Obtenemos el diario donde se registrara el pago de Detracción
                    journal = self.env['account.journal'].search([('is_detraction', '=', True)], limit=1)
                    if not journal:
                        journal = self.env['account.journal'].search([], limit=1)
                    moneda_venta = self.env['res.currency'].search([('name', 'like', 'PEN'), ('type', 'like', 'sale')],
                                                                   limit=1)
                    if moneda_venta:
                        currency = moneda_venta.id
                    else:
                        currency = res.get('values')[0].get('currency_id')
                # 0001 - Fin
                else:
                    journal = self.journal_id
                    banco = bank_factura
                    currency = res.get('values')[0].get('currency_id')
                    Tipo_Pago = self.payment_methods_id

                # Pago 1
                pay_val = {
                    'payment_type': self.payment_type,
                    'payment_date': payment_date,
                    'partner_type': self.partner_type,
                    'payment_for': 'multi_payment',
                    'partner_id': res.get('partner_id'),
                    'journal_id': journal and journal.id or False,
                    'communication': self.communication,
                    'payment_method_id': payment_method_id and payment_method_id.id or False,
                    'state': 'draft',
                    'type': tipo,
                    'payment_methods_id': Tipo_Pago and Tipo_Pago.id or False,
                    'back_partner_id': banco and banco.id or False,
                    'currency_id': currency,
                    'amount': 0.0,
                }
                payment_id1 = self.env['account.payment'].create(pay_val)

                # Montos
                paid_amt1 = 0
                paid_amt2 = 0
                if is_retencion:
                    paid_amt1 = round(inv_line.get('paid_amount') * 0.03, 2)
                    paid_amt2 = inv_line.get('paid_amount') - paid_amt1
                    paid_amt1 = paid_amt1 * invoice.exchange_rate
                # 0001 - Incio
                elif is_detraction_client:
                    paid_amt1 = round(inv_line.get('paid_amount') * (invoice.detrac_id.detrac * 0.01), 2)
                    paid_amt2 = round(inv_line.get('paid_amount') - paid_amt1, 2)
                    paid_amt1 = paid_amt1 * invoice.exchange_rate
                # 0001 - Fin
                else:
                    paid_amt1 = inv_line.get('paid_amount')

                full_reco1 = False
                full_reco2 = False

                # 0001 - Inicio - Modificado
                if is_retencion or is_detraction_client:
                    if invoice.residual == inv_line.get('paid_amount'):
                        full_reco2 = True
                # 0001 - Fin - Modificado
                else:
                    if invoice.residual == inv_line.get('paid_amount'):
                        full_reco1 = True

                line_list1 = []
                line_list1.append((0, 0, {
                    'invoice_id': invoice and invoice.id or False,
                    'account_id': invoice.account_id and invoice.account_id.id or False,
                    'date': invoice.date_invoice,
                    'due_date': invoice.date_due,
                    'original_amount': invoice.amount_total,
                    'balance_amount': invoice.residual,
                    'allocation': paid_amt1,
                    'full_reconclle': full_reco1,
                    'account_payment_id': payment_id1 and payment_id1.id or False
                }))

                payment_id1.write({
                    'line_ids': line_list1,
                    'amount': paid_amt1,
                    'invoice_ids': [(6, 0, inv_ids)]
                })

                # Pago 2
                # 0001 - Incio - Modificado
                if is_retencion or is_detraction_client:
                    # 0001 - Fin - Modificado
                    pay_val = {
                        'payment_type': self.payment_type,
                        'payment_date': payment_date,
                        'partner_type': self.partner_type,
                        'payment_for': 'multi_payment',
                        'partner_id': res.get('partner_id'),
                        'journal_id': self.journal_id and self.journal_id.id or False,
                        'communication': self.communication,
                        'payment_method_id': payment_method_id and payment_method_id.id or False,
                        'state': 'draft',
                        'type': 'factura',
                        'payment_methods_id': self.payment_methods_id and self.payment_methods_id.id or False,
                        'back_partner_id': bank_factura and bank_factura.id or False,
                        'currency_id': res.get('values')[0].get('currency_id'),
                        'amount': 0.0,
                    }
                    payment_id2 = self.env['account.payment'].create(pay_val)

                    line_list2 = []
                    line_list2.append((0, 0, {
                        'invoice_id': invoice and invoice.id or False,
                        'account_id': invoice.account_id and invoice.account_id.id or False,
                        'date': invoice.date_invoice,
                        'due_date': invoice.date_due,
                        'original_amount': invoice.amount_total,
                        'balance_amount': invoice.residual,
                        'allocation': paid_amt2,
                        'full_reconclle': full_reco2,
                        'account_payment_id': payment_id2 and payment_id2.id or False
                    }))

                    payment_id2.write({
                        'line_ids': line_list2,
                        'amount': paid_amt2,
                        'invoice_ids': [(6, 0, inv_ids)]
                    })
                    new_payment_ids.append(payment_id2)

                new_payment_ids.append(payment_id1)

        for pay in new_payment_ids:
            pay.post()

        return True


class bulk_inv_detraction(models.TransientModel):
    _name = 'bulk.inv.detraction'
    _description = "Pago de Detracciones"

    @api.model
    def default_get(self, fields):
        res = {}
        inv_ids = self._context.get('active_ids')
        vals = []
        invoice_ids = self.env['account.invoice'].browse(inv_ids)
        inv_type = ''
        for invo in invoice_ids:
            inv_type = invo.type
            break
        for inv in invoice_ids:
            if inv_type != inv.type:
                raise ValidationError('You must select only invoices or refunds.')
            if inv.state != 'open':
                raise ValidationError('Please Select Open Invoices.')
            # Inicio Codigo Optimiza
            if inv.detraccion_paid:
                raise ValidationError('Sólo facturas sin pago de detracción')
            if inv.hide_detraction:
                raise ValidationError('Sólo facturas con detracción')
            # Obtener Cuenta Bancaria
            cuenta_bank_detrac = ""
            for rec in inv.partner_id.bank_ids:
                if rec.is_detraction:
                    cuenta_bank_detrac = rec.bank_id.name + (" - " + rec.bank_id.bic if rec.bank_id.bic else "")
            # Fin Codigo Optimiza

            vals.append((0, 0, {
                'invoice_id': inv and inv.id or False,
                'partner_id': inv and inv.partner_id.id or False,
                'amount': inv.residual or 0.0,
                'bank_id': cuenta_bank_detrac or '',
                'paid_amount': inv.detraction_residual or 0.0,
            }))
            if inv.type in ('out_invoice', 'out_refund'):
                if not inv.hide_detraction:
                    raise ValidationError('Sólo Proveedores')
                res.update({
                    'partner_type': 'customer',
                })
            else:
                res.update({
                    'partner_type': 'supplier',
                })
        if inv_type in ('out_invoice', 'in_refund'):
            res.update({
                'payment_type': 'inbound'
            })
        else:
            res.update({
                'payment_type': 'outbound'
            })

        res.update({
            'invoice_ids': vals,
        })
        return res

    name = fields.Char('Name', default='hello')
    payment_type = fields.Selection(
        [('outbound', 'Send Money'), ('inbound', 'Receive Money'), ('transfer', 'Transfer')], string="Payment Type",
        required="1")
    payment_date = fields.Date('Payment Date', required="1")
    communication = fields.Char('Memo')
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Supplier')], string='Partner Type')
    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))])
    invoice_ids = fields.One2many('bulk.invoice', 'bulk_detraction_id', string='Invoice')

    @api.multi
    def process_payment(self):
        vals = []
        for line in self.invoice_ids:
            if line.paid_amount > 0.0:
                vals.append({
                    'invoice_id': line.invoice_id or False,
                    'partner_id': line.partner_id and line.partner_id.id or False,
                    'amount': line.amount or 0.0,
                    'paid_amount': line.paid_amount or 0.0,
                    'currency_id': line.invoice_id.currency_id.id or False,
                })
        new_vals = sorted(vals, key=itemgetter('partner_id'))
        groups = itertools.groupby(new_vals, key=operator.itemgetter('partner_id'))
        result = [{'partner_id': k, 'values': [x for x in v]} for k, v in groups]
        new_payment_ids = []

        # Inicio de Modificado
        num_lote = 0
        correlativo = 1
        pago_anterior = self.env['account.payment'].search([], order="id desc", limit=1)
        if pago_anterior.number_payment:
            num_lote = pago_anterior.number_payment + 1
        else:
            num_lote = 1
        # Fin de Modificado

        for res in result:

            payment_method_id = self.env['account.payment.method'].search([('name', '=', 'Manual')], limit=1)
            if not payment_method_id:
                payment_method_id = self.env['account.payment.method'].search([], limit=1)
            payment_date = False
            if self.payment_date:
                payment_date = self.payment_date.strftime("%Y-%m-%d")
            bank_detraccion = False
            proveedor = self.env['res.partner'].search([('id', 'like', res.get('partner_id'))], limit=1)
            for bank in proveedor.bank_ids:
                if bank.is_detraction and not bank_detraccion and not bank.is_retention:
                    bank_detraccion = bank

            for inv_line in res.get('values'):

                pay_val = {
                    'payment_type': self.payment_type,
                    'payment_date': payment_date,
                    'partner_type': self.partner_type,
                    'payment_for': 'multi_payment',
                    'partner_id': res.get('partner_id'),
                    'journal_id': self.journal_id and self.journal_id.id or False,
                    'communication': self.communication,
                    'payment_method_id': payment_method_id and payment_method_id.id or False,
                    'state': 'draft',
                    'number_payment': num_lote or 0,
                    'correlative_payment': correlativo or 0,
                    'type': 'detraccion',
                    'back_partner_id': bank_detraccion and bank_detraccion.id or False,
                    'currency_id': res.get('values')[0].get('currency_id'),
                    'amount': 0.0,
                }
                payment_id = self.env['account.payment'].create(pay_val)
                line_list = []
                paid_amt = 0
                inv_ids = []

                invoice = inv_line.get('invoice_id')
                inv_ids.append(invoice.id)
                full_reco = False
                if invoice.residual == inv_line.get('paid_amount'):
                    full_reco = True
                line_list.append((0, 0, {
                    'invoice_id': invoice.id,
                    'account_id': invoice.account_id and invoice.account_id.id or False,
                    'date': invoice.date_invoice,
                    'due_date': invoice.date_due,
                    'original_amount': invoice.amount_total,
                    'balance_amount': invoice.residual,
                    'allocation': inv_line.get('paid_amount'),
                    'full_reconclle': full_reco,
                    'account_payment_id': payment_id and payment_id.id or False
                }))
                paid_amt += inv_line.get('paid_amount')
                payment_id.write({
                    'line_ids': line_list,
                    'amount': paid_amt,
                    'invoice_ids': [(6, 0, inv_ids)]
                })
                #            payment_id.post()
                correlativo = correlativo + 1
                new_payment_ids.append(payment_id)
        for pay in new_payment_ids:
            pay.post()
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
