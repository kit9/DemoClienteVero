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
        #dominio = ([('line_ids.account_id.code', 'ilike', '121100')])
        #Filtro
        lst_account_move_line = self.env['account.move'].search([('line_ids.account_id.code', 'ilike', '121100')])

        # variables creadas
        content_txt = ""
        estado_ope = ""
        _catalogo = ""
        _fec_per = ""
        _resid = ""
        _ref = ""
        _fact = "INV"
        _sinFact = ""

        # Iterador
        for line in lst_account_move_line:

            # Catalogo
            if line.partner_id.catalog_06_id.code:
                _catalogo = line.partner_id.catalog_06_id.code

            # fecha del documento
            # if line.invoice_id.date_document:
            #     _fec_per = line.invoice_id.date_document

            #residual - importe adeudado
            for res in line.line_ids:
                if res.invoice_id.residual:
                    _resid = res.invoice_id.residual
                # for res1 in res.invoice_id:
                #     if res1.residual:
                #         _resid = res1.residual

                #si no hay factura
            for refer in line.line_ids:
                if refer.ref == _fact:
                    _sinFact = refer.ref
                else:
                    _sinFact = refer.statement_id.date
                                            



            #Estado de operacion
            if line.create_date.strftime("%m%Y") == time.strftime("%m%Y"):
                estado_ope = "01"
            else:
                if line.create_date.strftime("%Y") != time.strftime("%Y"):
                    estado_ope = "08"
                else:
                    if int(time.strftime("%Y")) == int(time.strftime("%Y")) - 2:
                        estado_ope = "09"
                    else:
                        estado_ope = "01"


            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.create_date.strftime("%Y/%m/%d") or '', #1 Periodo- Fecha contable
                line.ref or '',  # 2 ASIENTO CONTABLE
                line.x_studio_field_fwlP9 or '',  # 3 Asiento contable _ ID
                _catalogo or '', #4 ID - RUC
                line.partner_id.vat or '',  # 5 Tipo de Doc. Identidad - RUC, enteros
                line.partner_id.registration_name or '',  # 6 Nombre de la empresa
                _sinFact or '',  # 7
                _resid or '', # 8 importe adeudado
                estado_ope or '',
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
