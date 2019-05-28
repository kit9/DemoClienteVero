from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class ChartAccount(models.TransientModel):
    _name = "libreria.account_detail"
    _description = "Detalle Cuenta"

    # date_month = fields.Char(string="Mes", size=2)
    # date_year = fields.Char(string="Año", size=4)

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
        debe =""
        cuenta=""
        estado_ope = ""

        # Iterador
        for line in lst_account_move_line:

            for line1 in line.line_ids:
                debe = line1.debit
            #for line1 in line.dummy_account_id:
                #cuenta = line1.account_id.code

            # validador de estado de operación
            if line.create_date.strftime("%m%Y") == time.strftime("%m%Y"):
                estado_ope = "01"
            else:
                if line.create_date.strftime("%Y") != time.strftime("%Y"):
                    estado_ope = "08"
                else:
                    if int(time.strftime("%m")) == int(time.strftime("%m")) - 1:
                        estado_ope = "00"
                    else:
                        estado_ope = "01"

            # datos a exportar a txt

            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.create_date.strftime("%Y%m00") or '',  # Periodo
                line.name or '',  #
                line.x_studio_field_fwlP9 or '',  #
                line.invoice_id.partner_id.catalog_06_id.code or'',  #
                line.invoice_id.partner_id.vat or '',  #
                line.invoice_id.partner_id.registration_name or'',  #
                line.invoice_id.document_type_id.number or'',  #
                line.invoice_id.invoice_serie or'',  #
                line.invoice_id.invoice_number or '',  #
                line.invoice_id.date_document.strftime("%d/%m/%Y") or '',  #
                debe or '',  #
                line.dummy_account_id.code or ''   # estado de operacion

            )

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
