from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class chartofaccounts(models.TransientModel):
    _name = "libreria.not_domiciled"
    _description = "No Domiciliados"

    state = fields.Selection(
        [('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        # Data - Jcondori

        lst_account_move_line = self.env['account.invoice'].search([])
        content_txt = ""
        # Iterador - Jcondori
        for line in lst_account_move_line:
            # Asiento Conta

            # por cada campo encontrado daran una linea como mostrare
            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                           # Facturas de proveedor
                           line.date_invoice or '',  # 1 Hoja 1 (Fecha Contable)
                           line.move_id.x_studio_field_fwlP9 or '',  # 2 Hoja 2 (Asiento Contable/ID)
                           line.move_id or '',  # 3 Hoja 3 (Asiento Contable)
                           line.date_document or '',  # 4 Hoja 4 (Fecha de Documento)
                           line.document_type_id or '',  # 5 Hoja 5 (Tipo de Documento)
                           line.invoice_serie or '',  # 6 Hoja 6 (Serie)
                           line.invoice_number or '',  # 7 Hoja 7 (Numero)
                           line.base_imp or '',  # 8 Hoja 8 (Base Imponible)
                           '',  # 9 Hoja 8 (Tipo de Cambio
                           line.amount_total or '',  # 10 Hoja 10 (Total)
                           line.exchange_rate or '',  # 11 Hoja 10 (Tipo de Cambio)
                           '',  # 12 Hoja 11 (Tipo de persona: natural-juridica)
                           line.invoice_number or '',  # 13 Hoja 12 (Numero)
                           line.year_emission_dua or '',  # 14 Hoja 13 (Año de la Emision de la DUA)
                           '',  # 15 Hoja
                           '',  # 16 Hoja
                           '',  # 17 Hoja
                           '',  # 18 Hoja
                           '',  # 19 Hoja
                           '',  # 20 Hoja
                           '',  # 21 Hoja
                           '',  # 22 Hoja
                           '',  # 23 Hoja
                           '',  # 24 Hoja
                           '',  # 25 Hoja
                           '',  # 26 Hoja
                           '',  # 27 Hoja
                           '',  # 28 Hoja
                           '',  # 29 Hoja
                           '',  # 30 Hoja
                           '',  # 31 Hoja
                           '',  # 32 Hoja
                           '',  # 33 Hoja
                           '',  # 34 Hoja
                           '',  # 35 Hoja
                           ''  # 36 Hoja

            )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "No_Domiciliados.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'No Domiciliados',
            'res_model': 'libreria.not_domiciled',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }