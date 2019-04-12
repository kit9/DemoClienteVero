from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class not_domiciled(models.TransientModel):
    _name = "libreria.not_domiciled"
    _description = "No Domiciliados"

    date_month = fields.Char(string="Mes", size=2)
    date_year = fields.Char(string="Año", size=4)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        # Data - Jcondori

        lst_account_move_line = self.env['account.invoice'].search([
            ('month_year_inv', 'like', self.date_month + "" + self.date_year)
            #('partner_id.person_type', 'like', 'Persona')
        ])
        content_txt = ""
        estado_ope = ""
        tip_imp = "" # Tipo de impuesto
        tip_Prov = "" # Tipo de proveedor
        serie_Comp = "" # serie de comprobante de pago
        cantidad = "" # ... a pagar
        check = "" # ... este es para el apl. parrafo art.76
        value = "Otros Conceptos" # Si el impuesto dice Otros Conceptos
        valueProv = "03-Sujeto no Domiciliado" # Si el proveedor es no domiciliado
        # No Domiciliado  -- 18 al 25
        pais_ND = ""
        Proveedor_ND = ""
        domicilio_ND = ""
        NIF_ND = ""
        NIF_Benf = ""
        Proveedor_Benf = ""
        pais_Benf = ""
        Vinculo = ""

        # Iterador - Jcondori
        for line in lst_account_move_line:

            for imp in line.invoice_line_ids:
                for imp1 in imp.invoice_line_tax_ids:
                    # H9 cuando el impuesto (Value) sea Otros Conceptos, multiplicar Total con Tipo de Cambio
                    if imp1.name == value:
                        tip_imp = line.amount_untaxed * line.exchange_rate
                    else:
                        tip_imp = ""
                        #tip_imp = imp1.name

            for p2 in line.payment_ids:
                cantidad = sum(line.amount for line in line.payment_ids) # H15 Sumar la cantidad de registros que haya

                if line.message_needaction: # Si el Checkbox esta marcado, colocar 1, sino dejar en blanco
                    check = "1"
                else:
                    check = ""
            # si el proveedor es distinto a NO DOMICILIADO, mostrar el tipo de proveedor que es y su serie de comp. pago
            if line.partner_id.person_type != valueProv:
                tip_Prov = line.partner_id.person_type
                serie_Comp = line.invoice_number
            else:
                if line.partner_id.person_type == valueProv:
                tip_Prov = ""
                serie_Comp = ""
                pais_ND = line.partner_id.country_id.name
                Proveedor_ND = line.partner_id.commercial_company_name
                domicilio_ND = line.partner_id.street
                NIF_ND = line.partner_id.vat
                NIF_Benf = line.partner_id.mobile
                Proveedor_Benf = line.partner_id.name
                pais_Benf = line.partner_id.country_id.name
                Vinculo = line.partner_id.title.id


                # Asiento Contable
            if line.create_date.strftime("%m%Y") == time.strftime("%m%Y"):
                estado_ope = "1"
            else:
                if line.create_date.strftime("%Y") != time.strftime("%Y"):
                    estado_ope = "0"
                else:
                    estado_ope = "0"

            # Hay 10,10,10,7
            txt_line = "%s|M%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s" % (
                           # Proveedor / Facturas
                           line.date_invoice.strftime("%Y%m00") or '',  # C1 H1(Fecha Contable)
                           line.move_id.x_studio_field_fwlP9 or '',  # C2 H2(Asiento Contable/ID)
                           line.move_id.ref or '',  # C3 H3(Asiento Contable)
                           line.date_document.strftime("%d/%m/%Y") or '',  # C4 H4(Fecha de Documento)
                           line.document_type_id.number or '',  # C5 H5(Tipo de Documento)
                           line.invoice_serie or '',  # C6 H6(Serie de comp. pago o doc.)
                           line.invoice_number or '',  # C7 H7(Numero de comp. pago o doc.)
                           line.amount_untaxed * line.exchange_rate or '',  # C8 H8(BImp *TCambio ----- valor de las adquisiciones)
                           tip_imp or '',  # C9 H9(Otros Conceptos Adicionales)
                           line.amount_total * line.exchange_rate or '',  # C10 H10(Total * Tipo de Cambio --- Imp. total de las adq. regstr)
                           # 11 y 12 se llena cuando es distinta a NO DOMICILIADO
                           tip_Prov or '',  #C11 H11  (Tipo de persona: natural-juridica)
                           serie_Comp or '',  # C12 H12(Numero)
                           line.year_emission_dua or '',  #C13 H13(Año de la Emision de la DUA)
                           line.invoice_number or '',  # C14 H14(Numero)
                           cantidad or '',  # C15 H15(Cantidad a Pagar --- Monto de retencion del IGV)
                           # line.state or '',  #H15 (Estado)
                           line.currency_id.name or '',  # C16 (Codigo de la moneda / TABLA 4)
                           line.exchange_rate or '',  # C17 (Tipo de Cambio)
                           # 18 al 25 se llena si el proveedor es No Domiciliado
                           pais_ND or '',  # C18 H18(Pais)
                           Proveedor_ND or '',  # C19 H19(Proveedor)
                           domicilio_ND or'',  # C20 H20 (Address)
                           NIF_ND or '',  # C21 H21(RUC, NIF - NIF No Domiciliado)
                           # Beneficiario de los Pagos
                           NIF_Benf or '',  # C22 H22 NIF - NIF Beneficiario)
                           Proveedor_Benf or '',  # C23 H23(Nombre de Contacto)
                           pais_Benf or '',  # C24 (Pais)
                           Vinculo or '',  # C25  (Vinculo Contribuyente y residente en el extranjero -- si es socio ..)
                           '',  # C26 H26 null (Renta Bruta)
                           '',  # C27 H27 null (Deduccion/Costo de Enajenacion de bienes de Capital)
                           '',  # C28 H28 null (Renta Neta)
                           '',  # C29 H29 null (Tasa de Retencion)
                           '',  # C30 H30 null (Impuesto Retenido)
                           line.partner_id.x_studio_convenios or '',  # C31 H31 (Convenios --- evitar la doble imposicion)
                           line.x_studio_exoneraciones or '',  # C32 Hoja 32 (Exoneraciones)
                           line.type_income_id.number or '',  # C33 Hoja 33 (tipo de renta)
                           line.x_studio_modalidad_de_servicio or '',  # C34 H34 (Modalidad de Servicio)
                           check or '',  # C35 H35  (Aplicacion parrafo art. 76, marcado = 1, sino blanco)
                           estado_ope or '',  # C36 H36 (Estado identifica la anotacion o indicacion)
                           '|',  # C37 campos de libre utilizacion

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
