########################################################################################################################
# -- OPTIMIZA                                                                                                          #
# -- DESCRIPCION: CUENTA 14 CREACION PARA PROYECTO ODOO                                                                #
# -- AUTOR: ANTHONY ROBINSON LOAYZA PEREZ                                                                              #
# -- CAMBIOS: ID     FECHA (DD/MM/YYYY)  PERSONA               CAMBIOS EFECTUADOS                                      #
# --          #001   05/06/2019          ANTHONY LOAYZA        CREACION DE LA CLASE.                                   #
# --          #002   05/06/2019          ANTHONY LOAYZA        AGREGADO DE CAMPOS CON CONDICIONALES.                   #
# --          #003   05/06/2019          ANTHONY LOAYZA        AGREGANDO CAMPOS.                                       #
# --          #004   05/06/2019          ANTHONY LOAYZA        CONVIRTIENDO TXT A BINARIO.                             #
# --          #005   26/06/2019          ANTHONY LOAYZA        MODIFICADO EL MODELO A BUSCAR CON FILTRO.               #
# --          #006   26/06/2019          ANTHONY LOAYZA        AGREGADO DE VALIDADOR DE ERROR.                         #
# --          #007   26/06/2019          ANTHONY LOAYZA        MODIFICADO LA CONDICIONAL DEBIT.                        #
# ######################################################################################################################

from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)

    # INICIO 001 "CREACION DE LA CLASE"
class Account_14(models.TransientModel):
    _name = "libreria.account_46"
    _description = "Cuenta_46"

    date_year = fields.Char(string="Año", size=4)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    # FIN 001

    @api.multi
    def generate_file(self):

    # INICIO 005 "MODIFICADO EL MODELO A BUSCAR CON FILTRO"

        # modelo a buscar
        lst_account_move_line = self.env['account.move.line'].search([('year_move_line', '=', self.date_year),
                                                                      ('account_id.code', 'like', '46')])

    # FIN 005

        # variables creadas
        content_txt = ""
        _estado_ope = ""
        _credi = ""


    # INICIO 002 "AGREGADO DE CAMPOS CON CONDICIONALES"

        # Iterador
        for line in lst_account_move_line:

            if line.balance_cash_basis == 0:
                0
            else:
                if line.balance_cash_basis != 0:
                    content_txt



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

    # FIN 002

    # INICIO 003 "AGREGANDO CAMPOS"

            # datos a exportar a txt

            txt_line = "%s|%s|M%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.date.strftime("%Y%m%d") or '',  # 1
                line.move_id.name or '',
                line.id or '',
                line.partner_id.catalog_06_id.code or '',
                line.partner_id.vat or '',
                line.invoice_id.date_document or '',
                line.partner_id.name or '',
                line.account_id.code or '',
                - line.debit or line.credit,
                _estado_ope or ''
            )

    # FIN 003

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

    # INICIO 004 "CONVIRTIENDO TXT A BINARIO"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Cuenta_46.txt"
        })
    # FIN 004

        return {
            'type': 'ir.actions.act_window',
            'name': 'Cuenta_46',
            'res_model': 'libreria.account_46',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
# Fin