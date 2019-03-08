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
        lst_account_move_line = self.env['account.account'].search([])

        content_txt = ""

        # Iterador - Jcondori
        for line in lst_account_move_line:
            # Asiento Conta
            # por cada campo encontrado daran una linea como mostrare
            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                           line.create_date.strftime("%Y%m00") or '',
                           '', '', '', '', '', '', '', '',
                           '', '', '', '', '', '', '', '', '',
                           '', '', '', '', '', '', '', '', '',
                           '', '', '', '', '', '', '', '', ''

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
