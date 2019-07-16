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
# --          #008   15/07/2019          JOSE CONDORI          CORRECCION DE ERROR CON FECHA.                          #
# ######################################################################################################################

from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


# INICIO 001 "CREACION DE LA CLASE"
class Sales(models.TransientModel):
    _name = "libreria.sales"
    _description = "Sales"

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    # FIN 001

    @api.multi
    def generate_file(self):

        # modelo a buscar
        lst_account_move_line = self.env['account.invoice'].search([])

        # INICIO 006 "AGREGADO DE VALIDADOR DE ERROR"

        # validador de error
        # if len(lst_account_move_line) == 0:
        #    raise ValidationError("No se encuentra la venta")

        # FIN 006

        # variables creadas
        content_txt = ""
        _pay = ""

        # INICIO 002 "AGREGADO DE CAMPOS CON CONDICIONALES"

        # Iterador
        for line in lst_account_move_line:

            # _payments
            if len(line.payment_ids) > 0:
                _pay = "1"
            else:
                _pay = ""

            # INICIO 003 "AGREGANDO CAMPOS"

            # datos a exportar a txt

            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                # 008 - Incio - Coreccion de error con campo fecha
                line.date_document.strftime("%d-%m-%Y") if line.date_document else "",  # 1
                # line.date_document.strftime("%d-%m-%Y") if self.date_document else "",  # 1
                # 008 - Fin - Coreccion de error con campo fecha
                line.number or '',  # 2
                line.move_id.x_studio_field_fwlP9 or '',  # 3
                line.date_invoice or '',  # 4
                line.date_due or '',  # 5
                line.document_type_id.id or '',  # 6
                line.invoice_serie or '',  # 7
                line.invoice_number or '',  # 8
                '',  # 9
                line.partner_id.catalog_06_id.code or '',  # 10
                line.partner_id.vat or '',  # 11
                line.partner_id.name or '',  # 12
                '',  # 13
                line.amount_untaxed or '',  # 14
                '',  # 15
                line.amount_tax or '',  # 16
                '',  # 17
                '',  # 18
                '',  # 19
                '',  # 20
                '',  # 21
                '',  # 22
                '',  # 23
                line.amount_total or '',  # 24
                line.currency_id.name or '',  # 25
                line.exchange_rate or '',  # 26
                line.date_invoice or '',  # 27
                line.document_type_id.id or '',  # 28
                line.invoice_serie or '',  # 29
                line.invoice_number or '',  # 30
                '',  # 31
                '',  # 32
                _pay or '',  # 33
                '1',  # 34
                '',  # 35
            )

            # FIN 003

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        # INICIO 004 "CONVIRTIENDO TXT A BINARIO"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "venta.txt"
        })
        # FIN 004

        return {
            'type': 'ir.actions.act_window',
            'name': 'sales',
            'res_model': 'libreria.sales',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
# Fin
