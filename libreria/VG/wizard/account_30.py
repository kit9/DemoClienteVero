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

        # modelo a buscar
        lst_account_move_line = self.env['account.move'].search([])

        # variables creadas
        content_txt = ""

        # Iterador
        for line in lst_account_move_line:


            # datos a exportar a txt

            txt_line = "%s|%s|M%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.date.strftime("%Y%m00") or '',  # 1 fecha en formato codigo
                line.name.replace("/", "") or '', #2 nombre de la factura
                line.x_studio_field_fwlP9 or '', #3 codigo de almacenamiento
                _catalogo or '', #4 codigo de la compañia a quien se brindo el servicio
                line.partner_id.vat or '', #5 ruc de la empresa
                line.partner_id.name or '', #6 nombre de la empresa
                line.date.strftime("%d/%m/%Y") or '', #7 fecha de elaboración
                cantidad or '', #8 total de monto a cobrar
                estado_ope or '',
                '',
            )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Ple. Cuenta 30.txt"
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
