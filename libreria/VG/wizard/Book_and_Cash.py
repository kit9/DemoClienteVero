from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)

###########################################################################################
# -- OPTIMIZA
# -- DESCRIPCION: CLASE CHART_ACCOUNT CREACION PARA PROYECTO ODOO
# -- AUTOR: JORDY VALENZUELA VALCARCEL
# -- CAMBIOS: ID     FECHA (DD/MM/YYYY)  PERSONA               CAMBIOS EFECTUADOS
# --          #001   13/03/2019          JORDY VALENZUELA          CREACION DE LA CLASE.
# --          #002   13/03/2019          JORDY VALENZUELA          AGREGADO DE CAMPOS
# --          #003   13/03/2019          JORDY VALENZUELA          VALIDACION DE CAMPOS
# --          #004   13/03/2019          JORDY VALENZUELA          AGREGADO DE FILTROS.
# -----------------------------------------------------------------------------------------

#   Inicio #001 "CREACION DE LA CLASE"
class Book_and_Cash(models.TransientModel):
    _name = "libreria.Book_and_Cash"
    _description = "Libro Caja y Bancos"


#   Inicio #004 "AGREGADO DE FILTROS"
#     date_month = fields.Selection(string="Mes", selection=[('01', 'Enero'),
#                                                            ('02', 'Febrero'),
#                                                            ('03', 'Marzo'),
#                                                            ('04', 'Abril'),
#                                                            ('05', 'Mayo'),
#                                                            ('06', 'Junio'),
#                                                            ('07', 'Julio'),
#                                                            ('08', 'Agosto'),
#                                                            ('09', 'Septiembre'),
#                                                            ('10', 'Octubre'),
#                                                            ('11', 'Noviembre'),
#                                                            ('12', 'Diciembre')])
#     date_year = fields.Char(string="Año", size=4)
#   Fin #004

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):

        # filtro de fecha
        #dominio = [('month_year_inv', 'like', self.date_month + "" + self.date_year)]

        # modelo a buscar
        lst_account_move_line = self.env['account.move'].search([])

        # variables creadas
        content_txt = ""
        cuenta = ""
        moneda = ""
        # Inicio #003 "VALIDACION DE CAMPOS"
        for line in lst_account_move_line:
            # validador de campo vacio
            if line.line.ids:
                cuenta = line.account_id.code
            if line.line.ids:
                moneda = line.currency_id.name

        # Fin #003
            # datos a exportar a txt
            # Inicio #002 "AGREGADO DE CAMPOS"
            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.date.strftime("%Y%m00") or '',  # Periodo
                line.name or '',  # codigo cuenta
                line.id or '',  #
                cuenta or '',  # cuenta
                '',  # vacio
                '',  # vacio
                moneda or '',  # moneda
                '',  #
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                ''
            )
            # Fin #002

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Libro Caja y Bancos.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Libro Caja y Bancos',
            'res_model': 'libreria.Book_and_Cash',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
#   Fin #001
