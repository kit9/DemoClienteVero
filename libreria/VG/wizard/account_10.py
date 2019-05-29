from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class account_10(models.TransientModel):
    _name = "libreria.account_10"
    _description = "account_10"

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):

        # modelo a buscar
        lst_account_move_line = self.env['account.payment'].search([])

        # variables creadas
        content_txt = ""
        cuent_banc = ""

        # Iterador
        for line in lst_account_move_line:
            for imp in line.payment_ids:
                if imp.bank_account_id.acc_number:
                    cuent_banc = imp.bank_account_id.acc_number

            # datos a exportar a txt
            txt_line = "%s|%s|%s|%s|%s|%s|%s|" % (
                line.payment_date.strftime("%Y%m00") or '',
                '',
                line.journal_id.code or'',
                cuent_banc or'',
                '',
                '',
                ''
            )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Cuenta_10.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'account_10',
            'res_model': 'libreria.account_10',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }