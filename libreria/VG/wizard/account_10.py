from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class Account_10(models.TransientModel):
    _name = "libreria.account_10"
    _description = "Cuenta_10"

    #date_month = fields.Char(string="Mes", size=2)
    #date_year = fields.Char(string="Año", size=4)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):

        # modelo a buscar
        lst_account_move_line = self.env['account.invoce'].search([])

        # variables creadas
        content_txt = ""
        estado_ope = ""
        catalogo = ""



        # Iterador
        for line in lst_account_move_line:
            # Catalogo
            for imp1 in line.line_ids:
                if imp1.partner_id.catalog_06_id:
                 catalogo = imp1.partner_id.catalog_06_id


            # datos a exportar a txt

            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (

                line.journal_id or'',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                ''
            )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Cuenta_10.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cuenta_10',
            'res_model': 'libreria.account_10',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }