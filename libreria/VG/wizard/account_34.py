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
        lst_account_move_line = self.env['account.move'].search([('year_move', '=', self.date_year),
                                                                      ('line_ids.account_id.code', 'like', '34')])


        # variables creadas
        content_txt = ""
        _estado_ope = ""

        # Iterador
        for line in lst_account_move_line:

            if line.create_date.strftime("%m%Y") == time.strftime("%m%Y"):
                _estado_ope = "1"
            else:
                if line.create_date.strftime("%Y") != time.strftime("%Y"):
                    _estado_ope = "8"
                else:
                    if int(time.strftime("%m")) == int(time.strftime("%m")) - 1:
                        _estado_ope = "9"
                    else:
                        _estado_ope = "1"

            # datos a exportar a txt

            txt_line = "%s|%s|M%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.date.strftime("%Y/%m/%d") or '',
                line.name or '',
                line.x_studio_field_fwlP9 or '',
                line.asset_depreciation_ids or'',
                '',
                line.product_id or'',
                '',
                '',
                '',
                '',
                '',
                _estado_ope or '',
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