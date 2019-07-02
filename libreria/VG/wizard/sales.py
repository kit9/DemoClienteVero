
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
        lst_account_move_line = self.env['account.invoice'].search([('state', 'ilike', 'abierto')])

    # INICIO 006 "AGREGADO DE VALIDADOR DE ERROR"

        # validador de error
        if len(lst_account_move_line) == 0:
            raise ValidationError("No se encuentra la venta")

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
                _estado_ope = "1"
            else:
                if line.create_date.strftime("%Y") != time.strftime("%Y"):
                    _estado_ope = "8"
                else:
                    if int(time.strftime("%m")) == int(time.strftime("%m")) - 1:
                        _estado_ope = "9"
                    else:
                        _estado_ope = "1"


    # INICIO 003 "AGREGANDO CAMPOS"

            # datos a exportar a txt

            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.document_type_id or '',  # 1
                line.invoice_serie or '', # 2
                line.invoice_number or '', # 3
                line.type_ident or '', # 4
                line.num_ident or '', # 5
                line.inv_exonerada or '', # 6
                line.inv_amount_untax or '', # 7
                line.amount_untax or '', # 8
                line.inv_inafecto or '', # 9
                line.inv_isc or '', # 10
                line.inv_otros or '', # 11
                
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