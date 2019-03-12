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

        lst_account_move_line = self.env['account.payment'].search([])
        content_txt = ""
        estado_ope = ""
        # Iterador - Jcondori
        for line in lst_account_move_line:
            # Asiento Conta


            if line.create_date.strftime("%m%Y") == time.strftime("%m%Y"):
                estado_ope = "01"
            else:
                if line.create_date.strftime("%Y") != time.strftime("%Y"):
                    estado_ope = "09"
                else:
                    if int(time.strftime("%m")) == int(line.date.strftime("%m")) - 1:
                        estado_ope = "00"
                    else:
                        estado_ope = "09"

            # por cada campo encontrado daran una linea como mostrare
            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       (
                           line.payment_date("%Y%m00") or '', # 1
                           line.journal_id or '',  # 1
                           line.state or '',  # 1 null
                           #line.move_line_ids.move_id or '',  # 2
                           #line.move_line_ids.id or '',  # 3
                           line.payment_date("%Y%m00") or'',  # 4
                           line.partner_id.catalog_06_id or '',  # 5
                           line.partner_id.vat or '',  # 6
                           line.partner_id.name or '',  # 7
                           #'',  # 8
                           #'',  # 8
                           #'',  # 8
                           #''   # 9
                           estado_ope or ''   # 10

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
