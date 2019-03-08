from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class ConsolidatedJournal(models.TransientModel):
    _name = "sunat.chart_accounts"
    _description = "Diario Consolidado"

    state = fields.Selection(
        [('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):

        # Data
        lst_chart_accounts = self.env['account.account'].search([])

        content_txt = ""

        # Iterador
        for accounts in lst_chart_accounts:
            # Asiento Contable

            txt_line = "%s|%s" % (
                accounts.code or '',
                accounts.name or '',
            )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "diario_consolidado.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Diario Consolidado',
            'res_model': 'sunat.consolidated_journal',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
