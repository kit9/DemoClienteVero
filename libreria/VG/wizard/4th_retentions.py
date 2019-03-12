from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class chartofaccounts(models.TransientModel):
    _name = "libreria.chart_of_accounts"
    _description = "Plan Contable"

    state = fields.Selection(
        [('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        # Data - Jcondori

        lst_account_move_line = self.env['account.invoice'].search([])

        content_txt = ""
        estado_ope = ""

        # Iterador - Jcondori
        for line in lst_account_move_line:

            # Asiento Conta

            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.document_type_id or '', #1 jrejas
                line.type_ident or'', #2 jrejas
                line.num_ident or'', #3 jrejas
                line.document_type_id or'', #4 jrejas
                line.invoice_serie or'', #5 jrejas
                line.invoice_number or '', #6 jrejas
                line.residual.price_subtotal or'', #7 jrejas
                line.date_document  or'', #9 jrejas
                line.payment_ids.payment_date or'', #10 jrejas
                line.amount_tax.price_subtotal or'', #11 jrejas

            )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "plan_contable.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Plan Contable',
            'res_model': 'libreria.chart_of_accounts',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }