from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


    # INICIO 001 "CREACION DE LA CLASE"
class account_30(models.TransientModel):
    _name = "libreria.account_30"
    _description = "Cuenta_30"

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    # FIN 001

    @api.multi
    def generate_file(self):

    # INICIO 005 "MODIFICADO EL MODELO A BUSCAR CON FILTRO"

        # modelo a buscar
        lst_account_move_line = self.env['account.move.line'].search([('account_id.code', 'ilike', '30')])

    # FIN 005

        # variables creadas
        content_txt = ""
        _estado_ope = ""
        debe = ""
        _pago = ""

    # INICIO 002 "AGREGADO DE CAMPOS CON CONDICIONALES"

        # Iterador
        for line in lst_account_move_line:

            # debe
            #if len(line.debit) > 0:


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

            #ids campo debe


    # FIN 002

    # INICIO 003 "AGREGANDO CAMPOS"

            # datos a exportar a txt

            txt_line = "%s|%s|M%s|0%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.date.strftime("%Y/%m/%d") or '',  # 1
                line.partner_id.ref or '',
                line.x_studio_field_fwlP9 or '',
                line.partner_id.catalog_06_id.code or '',
                line.partner_id.vat or '',
                line.partner_id.name or '',
                '',
                '',
                '',
                '',
                '',
                _estado_ope or ''
            )

    # FIN 003

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

    # INICIO 004 "CONVIRTIENDO TXT A BINARIO"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Ple cuenta 30.txt"
        })
    # FIN 004

        return {
            'type': 'ir.actions.act_window',
            'name': 'Ple. cuenta 30',
            'res_model': 'libreria.account_30',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
# Fin