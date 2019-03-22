from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class chartofaccounts(models.TransientModel):
    _name = "libreria.retentions"
    _description = "Retenciones"

    state = fields.Selection(
        [('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        # Data - Jcondori

        lst_account_move_line = self.env['account.move','&',('id','=','30')].search([])
        content_txt = ""
        _factura = ""
        _numero = ""
        _total = ""
        _estado_ope = ""
        # Iterador - Jcondori
        for line in lst_account_move_line:
            # Asiento Conta

            # factura
            for imp in line.line_ids:
                if imp.invoice_id.id:
                    _factura = imp.invoice_id.id

            # numero
            for imp2 in line.line_ids:
                if imp2.invoice_id.invoice_number:
                   _numero = imp2.invoice_id.invoice_number

            #total
            for imp3 in line.line_ids:
                if imp3.invoice_id.amount_total:
                    _total = imp3.invoice_id.amount_total

            #10
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
            txt_line = "%s|%s|M%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.date.strftime("%Y%m00") or '',  # 1
                line.name or '',  # 2
                line.id or '',  # 3
                line.date or '',  # 4
                _factura or '', #5
                _numero or '', #6
                line.partner_id.name or '', #7
                _total or '', #8
                line.amount or '', #9
                _estado_ope or '', #10
                )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Retenciones.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Retenciones',
            'res_model': 'libreria.retentions',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
