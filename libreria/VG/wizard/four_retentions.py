from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class four_retentions(models.TransientModel):
    _name = "libreria.four_retentions"
    _description = "retenciones_4th"

    state = fields.Selection(
        [('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        # Data - Jcondori

        lst_account_move_line = self.env['account.invoice'].search([('document_type_id.id','like','2')])

        content_txt = ""
        estado_ope = ""

        # Iterador - Jcondori
        for line in lst_account_move_line:
            for imp in line.payment_ids:
                if imp.payment_date != "":
                    estado_ope = imp.payment_date

            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.document_type_id or '',
                line.display_name or '',  # 1 jrejas
                line.type_ident or '',  # 2 jrejas
                line.num_ident or '',  # 3 jrejas
                line.document_type_id.name or '',  # 4 jrejas
                line.invoice_serie or '',  # 5 jrejas
                line.invoice_number or '',  # 6 jrejas
                line.residual or '',  # 7 jrejas
                line.date_document or '',  # 9 jrejas
                estado_ope or '',  # 10 jrejas          5
                line.amount_tax or '',  # 11 jrejas

            )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "retenciones_4ta.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'retenciones_4ta',
            'res_model': 'libreria.four_retentions',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
