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

        lst_account_move_line = self.env['account.payment'].search([])
        content_txt = ""
        _estado_ope = ""
        _locaciones = ""
        _asiento = ""
        _codigo = ""
        _factura = ""
        # Iterador - Jcondori
        for line in lst_account_move_line:
            # Asiento Conta

            # allocation
            for imp in line.line_ids:
                if imp.allocation != "":
                    _locaciones = imp.allocation

            # asiento contable
            for imp1 in line.move_line_ids:
                if imp1.move_id != "":
                    _asiento = imp1.move_id

            # id
            for imp2 in line.move_line_ids:
                if imp2.id != "":
                    _codigo = imp2.id

            # factura
            for imp3 in line.move_line_ids:
                if imp3.invoice_id != "":
                    _factura = imp3.invoice_id.amount_total * imp3.invoice_id.exchange_rate

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
            txt_line = "%s|%s|%s|%s|M%s|%s|%s|%s|%s|%s|%s|%s" % (
                    line.payment_date.strftime("%Y%m00") or '',  # 1
                    line.journal_id or '',  # 1
                    line.state or '',  # 1 null
                    _asiento or '',  # 2
                    _codigo or '',  # 3
                    line.payment_date or '',  # 4
                    line.partner_id.catalog_06_id or '',  # 5
                    line.partner_id.vat or '',  # 6
                    line.partner_id.name or '',  # 7
                    _factura or '',  # 8 #
                    _locaciones or '',  # 9
                    _estado_ope or ''  # 10
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
