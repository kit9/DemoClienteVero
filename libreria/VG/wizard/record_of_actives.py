from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class chartofaccounts(models.TransientModel):
    _name = "libreria.record_of_actives"
    _description = "Registro de Activos"

    state = fields.Selection(
        [('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        # Data - Jcondori
        # lst_account_move_line = self.env['account.move.line'].search([]) # Todo
        lst_account_move_line = self.env['account.asset.asset'].search([])

        content_txt = ""

        # Iterador - Jcondori
        for line in lst_account_move_line:
            # Asiento Conta
            # por cada campo encontrado daran una linea como mostrare
            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                           line.date("%Y%m00") or '',  # 1 jvalenzuela
                           line.code or'',  # 2 jvalenzuela
                           '',  # 3 jvalenzuela (no se encuentra)
                           '',  # 4 jvalenzuela (no se encuentra)
                           '',  # 5 rloayza
                           '',  # 6 rloayza
                           '',  # 7 rloayza
                           '',  # 8 rloayza
                           '',  # 9 rloayza
                           '',  # 10 rloayza
                           '',  # 11 ldelacruz
                           '',  # 12 ldelacruz
                           '',  # 13 ldelacruz
                           '',  # 14 ldelacruz
                           '',  # 15 null
                           '',  # 16 ldelacruz
                           '',  # 17 ldelacruz
                           '',  # 18 null
                           '',  # 19 null
                           '',  # 20 null
                           '',  # 21 null
                           '',  # 22 null
                           '',  # 23 jrejas
                           '',  # 24 jrejas
                           '',  # 25 jrejas
                           '',  # 26 null
                           '',  # 27 jrejas
                           '',  # 28 jrejas
                           '',  # 29 null
                           '',  # 30 null
                           '',  # 31 null
                           '',  # 32 null
                           '',  # 33 null
                           '',  # 34 null
                           '',  # 35 null
                           ''   # 36 jrejas

                       )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Registro_Activos.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Registro de Activos',
            'res_model': 'libreria.record_of_actives',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
