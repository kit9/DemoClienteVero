from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class not_domiciled(models.TransientModel):
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
        estado_ope = ""
        impuesto=""

        # Iterador - Jcondori
        for line in lst_account_move_line:
            for imp in line.invoice_line_ids:
                for imp1 in imp.invoice_line_tax_ids:
                    if imp1.name != "":
                        impuesto = imp1.name
            # Asiento Contable
            if line.create_date.strftime("%m%Y") == time.strftime("%m%Y"):
                estado_ope = "1"
            else:
                if line.create_date.strftime("%Y") != time.strftime("%Y"):
                    estado_ope = "0"
                else:
                    estado_ope = "0"

            # por cada campo encontrado daran una linea como mostrare , Hay 11,10,10,10
            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" \  
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                           # Facturas de proveedor
                           line.date_invoice or '',                     # 01 Hoja 1 (Fecha Contable)
                           line.move_id.x_studio_field_fwlP9 or '',     # 02 Hoja 2 (Asiento Contable/ID)
                           line.move_id or '',                          # 03 Hoja 3 (Asiento Contable)
                           line.date_document or '',                    # 04 Hoja 4 (Fecha de Documento)
                           line.document_type_id or '',                 # 05 Hoja 5 (Tipo de Documento)
                           line.invoice_serie or '',                    # 06 Hoja 6 (Serie)
                           line.invoice_number or '',                   # 07 Hoja 7 (Numero)
                           line.amount_untaxed or '',                   # 08 Hoja 8 (Base Imponible)
                           line.exchange_rate or '',                    # 09 Hoja 8 (Tipo de Cambio)
                           impuesto or '',                     # 10 Hoja 9 (Impuestos)
                           line.amount_untaxed or '',                   # 11 Hoja 9 (Base Imponible)
                           line.exchange_rate or '',                    # 12 Hoja 9 (Tipo de Cambio)
                           line.amount_total or '',                     # 13 Hoja 10 (Total)
                           line.exchange_rate or '',                    # 14  Hoja 10 (Tipo de Cambio)
                           line.partner_id.person_type or'',            # 15 Hoja 11 (Tipo de persona: natural-juridica)
                           line.invoice_number or '',                   # 16 Hoja 12 (Numero)
                           line.year_emission_dua or '',                # 17 Hoja 13 (Año de la Emision de la DUA)
                           line.invoice_number or '',                   # 18 Hoja 14 (Numero)
                           line.amount or '',                           # 19 Hoja 15 (Cantidad a Pagar)
                           line.state or '',                            # 20 Hoja 15 (Estado)
                           line.exchange_rate or '',                    # 21 Hoja 16 (Tipo de Cambio)
                           '',                                          # 22 Hoja 17 null
                           line.partner_id.country_id or'',             # 23 Hoja 18
                           line.partner_id or '',                       # 24 Hoja 19 (Proveedor)
                           line.partner_id.street or '',                # 25 Hoja 20 (Address, Direccion)
                           line.partner_id.catalog_06_id or'',          # 26 Hoja 21 (RUC)
                           '',                                          # 27 Hoja 22 null
                           line.partner_id.name or '',                  # 28 Hoja 23 (Nombre de Contacto)
                           line.partner_id.title or '',                 # 29 Hoja 24 (El contacto es : "socio")
                           '',                                          # 30 Hoja 25 null
                           '',                                          # 31 Hoja 26 null
                           '',                                          # 32 Hoja 27 null
                           '',                                          # 33 Hoja 28 null
                           '',                                          # 34 Hoja 29 null
                           '',                                          # 35 Hoja 30 null
                           line.partner_id.x_studio_convenios or '',    # 36 Hoja 31 (Convenios)
                           line.x_studio_exoneraciones or '',           # 37 Hoja 32 (Exoneraciones)
                           line.type_income_id or '',                   # 38 Hoja 33 (Hay dos tipos de renta: x_studio_tipo_de_renta, type_income_id)
                           line.x_studio_modalidad_de_servicio or '',   # 39 Hoja 34 (Modalidad de Servicio)
                           line.message_needaction or '',               # 40 Hoja 35 (Aplicacion parrafo art. 76)
                           estado_ope or ''                                           # 41 Hoja 36

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