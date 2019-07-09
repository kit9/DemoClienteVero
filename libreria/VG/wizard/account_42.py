from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)

#############################################################################################################
# -- OPTIMIZA
# -- DESCRIPCION: CLASE ACCOUNT_42 CREACION PARA PROYECTO ODOO
# -- AUTOR: LUIS A. DE LA CRUZ PELAEZ
# -- CAMBIOS: ID     FECHA (DD/MM/YYYY)  PERSONA               CAMBIOS EFECTUADOS
# --          #001   09/07/2019          LUIS DE LA CRUZ          CREACION DE LA CLASE
# --          #002   09/07/2019          LUIS DE LA CRUZ          AGREGADO DE CAMPOS CON CONDICIONALES
# --          #003   09/07/2019          LUIS DE LA CRUZ          AGREGADO DE CAMPOS
# --          #004   09/07/2019          LUIS DE LA CRUZ          VALIDACION DE CAMPOS
# --          #005   09/07/2019          LUIS DE LA CRUZ          CONVIRTIENDO TXT A BINARIO
# -----------------------------------------------------------------------------------------

#   INICIO #001 "CREACION DE LA CLASE"
class Account_42(models.TransientModel):
    _name = "libreria.account_42"
    _description = "Cuenta_42"

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

#   FIN 001
    @api.multi
    def generate_file(self):

        # Filtro de Cuenta a buscar
        lst_account_move_line = self.env['account.move'].search([('line_ids.account_id.code', 'ilike', '421100')])

        #variables creadas
        content_txt = ""
        estado_ope = ""
        _catalogo = ""
        _importe = ""
        _value = "0.00"

#   INICIO 002 "AGREGADO DE CAMPOS CON CONDICIONALES" -- INICIO 004 "VALIDACION DE CAMPOS"
        #Iterador
        for line in lst_account_move_line:

            # Catalogo
            if line.partner_id.catalog_06_id.code:
                _catalogo = line.partner_id.catalog_06_id.code

            # Importe
            if line.debit >= _value:        # Debe > 0
                _importe = line.debit("+")  # ("+" monto)
            else                            # Haber > 0
                _importe = line.credit("-") # ("-" monto)

            #Estado de Operacion
            if line.create_date.strftime("%m%Y") == time.strftime("%m%Y"):
                estado_ope = "01"
            else:
                if line.create_date.strftime("%Y") != time.strftime("%Y"):
                    estado_ope = "08"
                else:
                    if int(time.strftime("%Y")) == int(time.strftime("%Y")) - 2:
                        estado_ope = "09"
                    else:
                        estado_ope = "01"
#   FIN 002 --- FIN 004

#   INICIO 003 "AGREGADO DE CAMPOS"
            # Datos a generar a TXT
            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.move_id.date.strftime("%Y/%m/%d") or '', # 01 Fecha
                line.move_id.name or '', # 02 Asiento Contable
                line.x_studio_field_fwlP9("M") or '', # 03 ID
                _catalogo or '', # 04 ID de Ruc
                line.partner_id.vat or '', # 05 Numero de Ruc
                line.date_maturity or '', # 06 Fecha de vencimiento
                line.partner_id.name or '', # 07 Nombre de Socio
                '', # 08 en blanco
                _importe or '', # 09 Debe o Haber
                estado_ope or '' # 10 Estado de Operacion
            )
#   FIN 003

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

#   INICIO 005 "CONVIRTIENDO TXT A BINARIO"
        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Cuenta_42.txt"
        })
#   FIN 005

        return {
            'type': 'ir.actions.act_window',
            'name': 'Cuenta_42',
            'res_model': 'libreria.account_42',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
