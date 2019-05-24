from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class retentions(models.TransientModel):
    _name = "libreria.retentions"
    _description = "Retenciones"

    date_month = fields.Char(string="Mes", size=2)
    date_year = fields.Char(string="Año", size=4)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        # Data - Jcondori

        lst_account_move_line = self.env['account.payment'].search(
            [('month_year_inv', '=', self.date_month + "" + self.date_year),
             ('journal_id.type', '=', 'retention')])

        content_txt = ""

        _logger.info(len(lst_account_move_line))

        # Iterador
        for line in lst_account_move_line:
            # por cada campo encontrado daran una linea como mostrare
            txt_line = "%s" % (
                    line.id or ""
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
