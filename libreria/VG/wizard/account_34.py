from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class account_34(models.TransientModel):
    _name = "libreria.account_34"
    _description = "Cuenta_34"

    date_year = fields.Char(string="Año", selection=[('01', '2019')])

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):

        # modelo a buscar
        lst_account_move_line = self.env['account.move.line'].search([('year_move_line', '=', self.date_year),
                                                                      ('account_id.code', 'like', '34')])


        # variables creadas
        content_txt = ""

        # Iterador
        for line in lst_account_move_line:


            # datos a exportar a txt

            txt_line = "%s|%s|M%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.date.strftime("%Y/%m/%d") or '',
                line.move_id.name or '',
                line.move_id.x_studio_field_fwlP9 or '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
            )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Ple. Cuenta 34.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ple. Cuenta 34',
            'res_model': 'libreria.account_34',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }