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
        impuesto = ""
        cantidad = ""
        check = ""

        # Iterador - Jcondori
        for line in lst_account_move_line:
            for imp in line.invoice_line_ids:
                for imp1 in imp.invoice_line_tax_ids:
                    if imp1.name:
                        impuesto = imp1.name
            for p2 in line.payment_ids:
                if p2.amount:
                    cantidad = p2.amount
                if line.message_needaction:
                    check = "1"
                # Asiento Contable
            if line.create_date.strftime("%m%Y") == time.strftime("%m%Y"):
                estado_ope = "1"
            else:
                if line.create_date.strftime("%Y") != time.strftime("%Y"):
                    estado_ope = "0"
                else:
                    estado_ope = "0"

            # por cada campo encontrado daran una linea como mostrare , Hay 10,10,10,9
            txt_line = "%s|M%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                # Facturas de proveedor
                line.date_invoice.strftime("%Y%m00") or '',  # 01 Hoja 1 (Fecha Contable)
                line.move_id.x_studio_field_fwlP9 or '',  # 02 Hoja 2 (Asiento Contable/ID)
                line.move_id.ref or '',  # 03 Hoja 3 (Asiento Contable)
                line.date_document or '',  # 04 Hoja 4 (Fecha de Documento)
                line.document_type_id.number or '',  # 05 Hoja 5 (Tipo de Documento)
                line.invoice_serie or '',  # 06 Hoja 6 (Serie)
                line.invoice_number or '',  # 07 Hoja 7 (Numero)
                line.amount_untaxed*line.exchange_rate or '',  # 08 Hoja 8 (Base Imponible*Tipo de Cambio)
                impuesto or '',  # 9 Hoja 9 (Impuestos)
                line.amount_untaxed*line.exchange_rate or '', #10 Hoja 9 (Base Imponible * Tipo de Cambio)
                line.amount_total*line.exchange_rate or '',  # 11 Hoja 10 (Total * Tipo de Cambio)
                line.exchange_rate or '',  # 12  Hoja 10 (Tipo de Cambio)
                line.partner_id.person_type or '',  # 13 Hoja 11 (Tipo de persona: natural-juridica)
                line.invoice_number or '',  # 14 Hoja 12 (Numero)
                line.year_emission_dua or '',  # 15 Hoja 13 (Año de la Emision de la DUA)
                line.invoice_number or '',  # 16 Hoja 14 (Numero)
                cantidad or '',  # 17 Hoja 15 (Cantidad a Pagar)
                line.state or '',  # 18 Hoja 15 (Estado)
                line.exchange_rate or '',  # 19 Hoja 16 (Tipo de Cambio)
                '',  # 20 Hoja 17 null
                line.partner_id.country_id.name or '',  # 21 Hoja 18
                line.partner_id.commercial_company_name or '',  # 22 Hoja 19 (Proveedor)
                line.partner_id.street or '',  # 23 Hoja 20 (Address, Direccion)
                line.partner_id.vat or '',  # 24 Hoja 21 (RUC, NIF)
                '',  # 25 Hoja 22 null
                line.partner_id.name or '',  # 26 Hoja 23 (Nombre de Contacto)
                line.partner_id.title.name or '',  # 27 Hoja 24 (El contacto es : "socio")
                '',  # 28 Hoja 25 null
                '',  # 29 Hoja 26 null
                '',  # 30 Hoja 27 null
                '',  # 31 Hoja 28 null
                '',  # 32 Hoja 29 null
                '',  # 33 Hoja 30 null
                line.partner_id.x_studio_convenios or '',  # 34 Hoja 31 (Convenios)
                line.x_studio_exoneraciones or '',  # 35 Hoja 32 (Exoneraciones)
                line.type_income_id.number or '', # 36 Hoja 33 (2 tipos de renta)
                line.x_studio_modalidad_de_servicio or '',  # 37 Hoja 34 (Modalidad de Servicio)
                check or '',  # 38 Hoja 35 (Aplicacion parrafo art. 76, marcado = 1, sino 0)
                estado_ope or ''  # 39 Hoja 36

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
