from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class Account_14(models.TransientModel):
    _name = "libreria.account_14"
    _description = "Cuenta_14"

    #date_month = fields.Char(string="Mes", size=2)
    #date_year = fields.Char(string="Año", size=4)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):

        # modelo a buscar
        lst_account_move_line = self.env['account.move'].search([('line_ids.account_id.code', 'ilike', '142200')])

        # variables creadas
        content_txt = ""
        _estado_ope = ""
        _debito=""
        _catalogo = ""
        _vat = ""

        # Iterador
        for line in lst_account_move_line:
            # _debito
            for imp in line.line_ids:
                if imp.amount_currency:
                    _debito = imp.amount_currency

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

            txt_line = "%s|%s|M%s|%s|%s|%s|%s|%s|%s" % (
                line.date.strftime("%Y%m00") or '',  # 1
                line.name.replace("/", "") or '',
                line.x_studio_field_fwlP9 or '',
                _catalogo or '',
                _vat or '',
                _nombre or '',
                line.date.strftime("%d/%m/%Y") or '',
                _debito or '',
                _estado_ope or ''
            )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Cuenta_14.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cuenta_14',
            'res_model': 'libreria.account_14',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
