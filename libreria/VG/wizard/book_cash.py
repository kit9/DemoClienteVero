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
    _name = "libreria.book_cash"
    _description = "Libro caja y bancos"

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):

# modelo a buscar
        dominio = [('name', 'like', 'CSH1')]

# modelo a buscar
        lst_account_move_line = self.env['account.move'].search(dominio)

# variables creadas
        content_txt = ""
        cuenta = ""
        moneda = ""
        factura = ""
        doc = ""
        serie = ""
        numero = ""
        debe = ""
        haber = ""
        # Inicio #003 "VALIDACION DE CAMPOS"
        for line in lst_account_move_line:
            # validador de campo vacio

            for line1 in line.line_ids:
                if line1.account_id.code == '101001':
                    cuenta = line1.account_id.code
            for line2 in line.line_ids:
                if line2.currency_id:
                    moneda = line2.currency_id.name
            for line3 in line.line_ids:
                if line3.payment_id:
                    factura = line3.payment_id
                    for imp in factura.invoice_ids:
                        if imp.number:
                            doc = imp.document_type_id.display_name
                        if imp.number:
                            serie = imp.invoice_serie
                        if imp.number:
                            numero = imp.invoice_number


            for line4 in line.line_ids:
                if line4.account_id.code == '101001':
                    debe= line4.debit
            for line4 in line.line_ids:
                if line4.account_id.code == '101001':
                    haber = line4.credit


        # Fin #003
            # datos a exportar a txt
            # Inicio #002 "AGREGADO DE CAMPOS"
            txt_line = "%s|%s|M%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.date.strftime("%Y%m00") or '',  # Periodo
                line.name or '',  # codigo cuenta
                line.id or '',  #
                cuenta or '',  # cuenta
                '',  # vacio
                '',  # vacio
                moneda or '',  # moneda
                doc or '',  # tipo de documento de factura proverdor
                serie or '',  # serie de factura proveedor
                numero or '',  # numero de factura proveedor
                line.date.strftime("%d/%m/%Y") or '',
                line.date.strftime("%d/%m/%Y") or '',
                line.date.strftime("%d/%m/%Y") or '',
                line.x_studio_glosa or '',
                '',
                debe or '0.00',
                haber or '0.00',
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
            'txt_filename': "Libro caja y bancos.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Libro caja y bancos',
            'res_model': 'libreria.book_cash',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
#   Fin #001
