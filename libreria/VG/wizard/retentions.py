from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class chartofaccounts(models.TransientModel):
    _name = "libreria.retentions"
    _description = "Retenciones"

    state = fields.Selection(
        [('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        # Data - Jcondori

        lst_account_move_line = self.env['account.invoice'].search([])
        content_txt = ""
        # Iterador - Jcondori
        for line in lst_account_move_line:
            # Asiento Conta

            # por cada campo encontrado daran una linea como mostrare
            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       (
                           line.date("%Y%m00") or '',  # 1 jvalenzuela
                           '',  # 18 null
                           '',  # 19 null
                           '',  # 20 null
                           '',  # 21 null
                           '',  # 29 null
                           '',  # 30 null
                           '',  # 31 null
                           '',  # 32 null
                           '',  # 33 null
                           '',  # 34 null
                           '',  # 35 null
                           ''   # 36 jrejas (no se encontro)

                       )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Retenciones.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Retenciones',
            'res_model': 'libreria.retentions',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
