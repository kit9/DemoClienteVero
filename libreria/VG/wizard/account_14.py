from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class retentions(models.TransientModel):
    _name = "libreria.account_14"
    _description = "Account_14"

    #date_month = fields.Char(string="Mes", size=2)
    #date_year = fields.Char(string="Año", size=4)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        # Data - Anthony
        #('month_year_move', 'like', self.date_month + "" + self.date_year)
        lst_account_move_line = self.env['account.move'].search([])

        content_txt = ""
        imp_numero = ""
        _estado_ope = ""
        _debito = ""

        _logger.info(len(lst_account_move_line))

        # Iterador
        for line in lst_account_move_line:
            # factura
            # for imp in line.line_ids:
            #     if imp.invoice_id:
            #         if imp.invoice_id.document_type_id:
            #             _factura = imp.invoice_id.document_type_id.number

             _debito
             for imp in line.line_ids:
                 if imp.debit:
                        _debito = debit

            # 10 valilador de estado de fecha
            if line.create_date.strftime("%m%Y") == time.strftime("%m%Y"):
                _estado_ope = "01"
            else:
                if line.create_date.strftime("%Y") != time.strftime("%Y"):
                    _estado_ope = "09"
                else:
                    if int(time.strftime("%m")) == int(line.date.strftime("%m")) - 1:
                        _estado_ope = "00"
                    else:
                        _estado_ope = "09"

            # por cada campo encontrado daran una linea como mostrare
            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.date.strftime("%Y%m00") or '',  # 1
                line.name or '',
                line.x_studio_field_fwlP9 or '',
                line.res.partner.catalog_06_id or '',
                line.res.partner.vat or '',
                line.res.partner.name or '',
                line.date or '',
                _debito or ''
            )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Account_14.txt"
        })



        return {
            'type': 'ir.actions.act_window',
            'name': 'Account_14',
            'res_model': 'libreria.account_14',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
