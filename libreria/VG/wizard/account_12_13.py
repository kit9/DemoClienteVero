from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class Account_12_13(models.TransientModel):
    _name = "libreria.account_12_13"
    _description = "Cuenta_12_13"

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):

        # modelo a buscar
        lst_account_move_line = self.env['account.move'].search([])

        # variables creadas
        content_txt = ""
        estado_ope = ""
        catalogo = ""



        # Iterador
        for line in lst_account_move_line:
            # Catalogo
            for imp1 in line.line_ids:
                if imp1.partner_id.catalog_06_id.code:
                    catalogo = imp1.partner_id.catalog_06_id.code

            # datos a exportar al txt

            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                '', #Hoja 2
                line.date_invoice.strftime("%Y%m00") or '', #1 Periodo- Fecha contable
                line.ref or '', #2 ASIENTO CONTABLE
                line.id or '', #3 Asiento contable _ ID
                catalogo or '', #4 ID - RUC
                line.partner_id.vat or '', #5 Tipo de Doc. Identidad - RUC, enteros
                line.partner_id.registration_name or '', #6 Nombre de la empresa
                line.date_document or '', #7
                line.residual or '', #8 importe adeudado
                ''

             )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Cuenta_12_13.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cuenta_12_13',
            'res_model': 'libreria.account_12_13',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }

