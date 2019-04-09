from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class retentions(models.TransientModel):
    _name = "libreria.retentions"
    _description = "Retenciones"

    date_month = fields.Char(string="Mes", size=2)
    date_year = fields.Char(string="Año", size=4)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        # Data - Jcondori

        lst_account_move_line = self.env['account.move'].search(
            [('month_year_move', 'like', self.date_month + "" + self.date_year),
             ('journal_id.name', 'ilike', 'Retenciones')])

        content_txt = ""
        imp_numero = ""
        _total = ""
        _estado_ope = ""
        #_factura = ""

        _logger.info(len(lst_account_move_line))

        # Iterador
        for line in lst_account_move_line:
            # factura
            # for imp in line.line_ids:
            #     if imp.invoice_id:
            #         if imp.invoice_id.document_type_id:
            #             _factura = imp.invoice_id.document_type_id.number

            # numero
            for imp2 in line.line_ids:
                if imp2.invoice_id.invoice_number:
                    imp_numero = imp2.invoice_id.invoice_number

            # total
            for imp3 in line.line_ids:
                if imp3.invoice_id.amount_total:
                    _total = imp3.invoice_id.amount_total

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
            txt_line = "%s|%s|M%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.date.strftime("%Y%m00") or '',  # 1
                line.name or '',  # 2
                line.id or '',  # 3
                line.date or '',  # 4
                #line.open_reconcile_view.content_txt1 or '',  # 5
                imp_numero or '',  # 6
                line.partner_id.name or '',  # 7
                _total or '',  # 8
                line.amount or '',  # 9
                _estado_ope or '',  # 10
                line.journal_id.name or ''
            )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

           #listando move.line
    # @api.multi
    # def generate_file(self):
        lst_account_move_line1 = self.env['account.move.line'].search([('journal_id.name', 'ilike', 'Retenciones')])

        content_txt1 = ""

        _logger.info(len(lst_account_move_line1))

        for line1 in lst_account_move_line1:

            txt_line1 = "%s" %(
                line1.id or ''
            )

            content_txt1 = content_txt1 + "" + txt_line1 + "\r\n"


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
