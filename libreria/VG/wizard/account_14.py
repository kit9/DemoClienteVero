
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
    _name = "libreria.account_14"
    _description = "Cuenta_14"

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    # FIN 001

    @api.multi
    def generate_file(self):

    # INICIO 005 "MODIFICADO EL MODELO A BUSCAR CON FILTRO"

        # --- Modificado el 26/06/2019 de ---
        # lst_account_move_line = self.env['account.move'].search([('line_ids.account_id.code', 'ilike', '141200')])
        # -- A
        # lst_account_move_line = self.env['account.move'].search([('line_ids.account_id.code', 'ilike', '1411')])

        # modelo a buscar
        lst_account_move_line = self.env['account.move'].search([('line_ids.account_id.code', 'like', '1411')])

    # FIN 005

    # INICIO 006 "AGREGADO DE VALIDADOR DE ERROR"

        # validador de error
        if len(lst_account_move_line) == 0:
            raise ValidationError("No se encuentra la cuenta 14")

    # FIN 006

        # variables creadas
        content_txt = ""
        _estado_ope = ""
        _debito=""
        _catalogo = ""
        _vat = ""

    # INICIO 002 "AGREGADO DE CAMPOS CON CONDICIONALES"

        # Iterador
        for line in lst_account_move_line:

    # INICIO 007 "MODIFICADO LA CONDICIONAL DEBIT"

            # Modificado el 26/06/2019 de
            # for imp in line.line_ids:
            #    if imp.amount_currency:
            #        _debito = imp.amount_currency

            # A

            # for imp in line.line_ids:
            #    if imp.debit:
            #        _debito = imp.debit

            # _debito
            for imp in line.line_ids:
                if imp.debit:
                    _debito = imp.debit
    #FIN 007

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

    # FIN 002

    # INICIO 003 "AGREGANDO CAMPOS"

            # datos a exportar a txt

            txt_line = "%s|%s|M%s|%s|%s|%s|%s|%s0|%s" % (
                line.date.strftime("%Y%m%d") or '',  # 1
                line.name.replace("/", "") or '',
                line.x_studio_field_fwlP9 or '',
                _catalogo or '',
                _vat or '',
                _nombre or '',
                line.date.strftime("%d/%m/%Y") or '',
                _debito or '',
                _estado_ope or ''
            )

    # FIN 003

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

    # INICIO 004 "CONVIRTIENDO TXT A BINARIO"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Libro Mayor Cuenta 14.txt"
        })
    # FIN 004

        return {
            'type': 'ir.actions.act_window',
            'name': 'Cuenta_14',
            'res_model': 'libreria.account_14',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
# Fin