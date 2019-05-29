from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class Account_17(models.TransientModel):
    _name = "libreria.account_17"
    _description = "Cuenta_17"

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):

        # modelo a buscar
        lst_account_move_line = self.env['account.move'].search([('line_ids.account_id.code', 'ilike', '17')])

        # variables creadas
        content_txt = ""
        estado_ope = ""
        _debito=""
        _catalogo = ""
        _vat = ""

        # Iterador
        for line in lst_account_move_line:
            # _debito
            for imp in line.line_ids:
                if imp.debit:
                    _debito = imp.debit

            # _catalogo
            for imp1 in line.line_ids:
                if imp1.partner_id.catalog_06_id.code:
                 _catalogo = imp1.partner_id.catalog_06_id.code

            # _vat
            for imp2 in line.line_ids:
                if imp2.partner_id.vat:
                   _vat = imp2.partner_id.vat

            # _nombre
            for imp3 in line.line_ids:
                if imp3.partner_id.name:
                   _nombre = imp3.partner_id.name

            # validador de estado de operación
            if line.create_date.strftime("%m%Y") == time.strftime("%m%Y"):
                estado_ope = "01"
            else:
                if line.create_date.strftime("%Y") != time.strftime("%Y"):
                    estado_ope = "09"
                else:
                    if int(time.strftime("%m")) == int(time.strftime("%m")) - 1:
                        estado_ope = "00"
                    else:
                        estado_ope = "01"

            # datos a exportar a txt

            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.date.strftime("%Y%m00") or '',  # 1
                line.name or '',
                line.x_studio_field_fwlP9 or '',
                line.partner_id.name or '',
                line.partner_id.vat or '',
                line.partner_id.name or '',
                line.date or '',
                '',
                '',
                '',
            )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Cuenta_17.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cuenta_17',
            'res_model': 'libreria.account_17',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
