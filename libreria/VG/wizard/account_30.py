from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class Account_17(models.TransientModel):
    _name = "libreria.account_30"
    _description = "Cuenta_30"

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        # filtro de fecha
        dominio = [('dummy_account_id.code', 'like', '30}')]

        # modelo a buscar
        lst_account_move_line = self.env['account.move'].search(dominio)

        # variables creadas
        content_txt = ""


        # Iterador
        for line in lst_account_move_line:



            # datos a exportar a txt

            txt_line = "%s|%s|M%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.date.strftime("%Y/%m/%d") or '',  # 1 fecha en formato codigo
                line.ref or '', #2 nombre de la factura
                line.x_studio_field_fwlP9 or '', #3 codigo de almacenamiento
                '', #4 codigo de la compañia a quien se brindo el servicio
                line.partner_id.vat or '', #5 ruc de la empresa
                line.partner_id or '', #6 nombre de la empresa
                '', #7 fecha de elaboración
                '', #8 total de monto a cobrar
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
            'txt_filename': "Ple. Cuenta 30"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ple. Cuenta 30',
            'res_model': 'libreria.account_30',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
