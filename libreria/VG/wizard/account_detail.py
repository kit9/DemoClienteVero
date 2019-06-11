from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


###########################################################################################
# -- OPTIMIZA
# -- DESCRIPCION: CLASE ACCOUNT_DETAIL CREACION PARA PROYECTO ODOO
# -- AUTOR: JORDY VALENZUELA VALCARCEL
# -- CAMBIOS: ID     FECHA (DD/MM/YYYY)  PERSONA               CAMBIOS EFECTUADOS
# --          #001   27/05/2019          JORDY VALENZUELA          CREACION DE LA CLASE.
# --          #002   27/05/2019          JORDY VALENZUELA          AGREGADO DE CAMPOS
# --          #003   27/05/2019          JORDY VALENZUELA          VALIDACION DE CAMPOS
# --          #004   27/05/2019          JORDY VALENZUELA          AGREGADO DE FILTROS.
# -----------------------------------------------------------------------------------------

#   Inicio #001 "CREACION DE LA CLASE"
class ChartAccount(models.TransientModel):
    _name = "libreria.account_detail"
    _description = "Detalle Cuenta"
#   Inicio #004 "AGREGADO DE FILTROS"
# --   date_month = fields.Char(string="Mes", size=2)
# ..   date_year = fields.Char(string="Año", size=4)
#   Fin #004
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):

# filtro de fecha
        dominio = [('dummy_account_id.code', 'like', '19')]

# modelo a buscar
        lst_account_move_line = self.env['account.move'].search(dominio)

# variables creadas
        content_txt = ""
        debe = ""
        cuenta = ""
        fecha = ""
        estado_ope = ""
# Inicio #003 "VALIDACION DE CAMPOS"
# Iterador
        for line in lst_account_move_line:

            for line1 in line.line_ids:
                debe = line1.debit
            if line.invoice_id.date_document:
                fecha = line.invoice_id.date_document
# validador de estado de operación
                if line.create_date.strftime("%m%Y") == time.strftime("%m%Y"):
                    estado_ope = "01"
                else:
                    if line.create_date.strftime("%Y") != time.strftime("%Y"):
                        estado_ope = "08"
                    else:
                        if int(time.strftime("%m")) == int(time.strftime("%m")) - 1:
                            estado_ope = "09"
                        else:
                            estado_ope = "01"
# Fin #003
# datos a exportar a txt
# Inicio #002 "AGREGADO DE CAMPOS"
            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.create_date.strftime("%Y%m00") or '',
                line.name or '',  #
                line.x_studio_field_fwlP9 or '',  #
                line.invoice_id.partner_id.catalog_06_id.code or '',  #
                line.invoice_id.partner_id.vat or '',  #
                line.invoice_id.partner_id.registration_name or '',  #
                line.invoice_id.document_type_id.number or '',  #
                line.invoice_id.invoice_serie or '',  #
                line.invoice_id.invoice_number or '',  #
                fecha.strftime("%d/%m/%Y") or '',  #
                debe or '',  #
                estado_ope or ''  # estado de operacion

            )
# Fin #002

# Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Detalle_Cuenta.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Detalle Cuenta',
            'res_model': 'libreria.account_detail',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
#   Fin #001
