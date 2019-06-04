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
        # ('dummy_account_id.code', 'like', 121100
        dominio = ([('line_ids.account_id.code', 'ilike', '121100')])

        lst_account_move_line = self.env['account.move'].search([dominio])

        # variables creadas
        content_txt = ""
        estado_ope = ""
        _catalogo = ""
        _fec_per = ""
        _residual = ""
        _ref = ""

        # Iterador
        for line in lst_account_move_line:

            # referencia - asiento contables
            #for imp in line.line_ids:
               # if imp.invoice_id:
                   # _ref = imp

            # Catalogo
            if line.partner_id.catalog_06_id.code:
                _catalogo = line.partner_id.catalog_06_id.code

            # fecha del documento
            if line.invoice_id.date_document:
                _fec_per = line.invoice_id.date_document

            #residual - importe adeudado

            #if line.invoice_id.residual:
                #_residual = line.invoice_id.residual

            #Asiento Contable
            if line.create_date.strftime("%m%Y") == time.strftime("%m%Y"):
                estado_ope = "1"
            else:
                if line.create_date.strftime("%Y") != time.strftime("%Y"):
                    estado_ope = "0"
                else:
                    estado_ope = "0"


            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.date.strftime("%Y%m00") or '', #1 Periodo- Fecha contable
                line.ref or '',  # 2 ASIENTO CONTABLE
                line.x_studio_field_fwlP9 or '',  # 3 Asiento contable _ ID
                _catalogo or '', #4 ID - RUC
                line.partner_id.vat or '',  # 5 Tipo de Doc. Identidad - RUC, enteros
                line.partner_id.registration_name or '',  # 6 Nombre de la empresa
                _fec_per or '',  # 7
                #_residual or '',  # 8 importe adeudado
                '',
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
