
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
        #if len(lst_account_move_line) == 0:
        #    raise ValidationError("No se encuentra la venta")

    # FIN 006

        # variables creadas
        content_txt = ""

    # INICIO 002 "AGREGADO DE CAMPOS CON CONDICIONALES"

        # Iterador
        for line in lst_account_move_line:

            # _nombre
            #for imp3 in line.line_ids:
            #    if imp3.partner_id.name:
            #       _nombre = imp3.partner_id.name

            # validador de estado de operación
            #if line.create_date.strftime("%m%Y") == time.strftime("%m%Y"):
            #    _estado_ope = "1"
            #else:
            #    if line.create_date.strftime("%Y") != time.strftime("%Y"):
            #        _estado_ope = "8"
            #    else:
            #        if int(time.strftime("%m")) == int(time.strftime("%m")) - 1:
            #            _estado_ope = "9"
            #        else:
            #            _estado_ope = "1"


    # INICIO 003 "AGREGANDO CAMPOS"

            # datos a exportar a txt

            txt_line = "%s|%s|%s|%s|%s|%s|%s" % (
                line.date_document or '',  # 1
                line.number or '',  # 2
                line.date_invoice or '',  # 3
                line.date_due or '',  # 4
                line.invoice_serie or '',  # 5
                line.document_type_id or '',  # 6
                line.invoice_number or '',  # 7
                #line.name.replace("/", "") or '',
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