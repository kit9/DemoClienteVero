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
        lst_account_move_line = self.env['account.invoice'].search([])

        # variables creadas
        content_txt = ""
        estado_ope = ""
        _catalogo = ""
        _fec_per = ""

        # Iterador
        for line in lst_account_move_line:
            # Catalogo
            # for imp1 in line.line_ids:
            #     if imp1.partner_id.catalog_06_id.code:
            #         _catalogo = imp1.partner_id.catalog_06_id.code

            for imp in line.einvoice_ids:
                for imp1 in imp.catalog.06:
                    if imp1.code:
                    _catalogo = imp1.code
            # line.invoice_id.partner_id.catalog_06_id.code
            # datos a exportar al txt
            # Fecha
            # if line.date_invoice:
            #     fec_per = line.invoice_id.date_invoice

            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.date.strftime("%Y%m00") or '',  # 1'', #1 Periodo- Fecha contable
                line.ref or '',  # 2 ASIENTO CONTABLE
                line.x_studio_field_fwlP9 or '',  # 3 Asiento contable _ ID
                _catalogo or '', #4 ID - RUC
                line.partner_id.vat or '',  # 5 Tipo de Doc. Identidad - RUC, enteros
                line.partner_id.registration_name or '',  # 6 Nombre de la empresa
                line.date_document or '',  # 7
                line.residual or '',  # 8 importe adeudado
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
