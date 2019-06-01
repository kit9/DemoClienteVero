from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class four_retentions(models.TransientModel):
    _name = "libreria.four_retentions"
    _description = "retenciones_4th"

    date_month = fields.Selection(string="Mes", selection=[('01', 'Enero'),
                                                           ('02', 'Febrero'),
                                                           ('03', 'Marzo'),
                                                           ('04', 'Abril'),
                                                           ('05', 'Mayo'),
                                                           ('06', 'Junio'),
                                                           ('07', 'Julio'),
                                                           ('08', 'Agosto'),
                                                           ('09', 'Septiembre'),
                                                           ('10', 'Octubre'),
                                                           ('11', 'Noviembre'),
                                                           ('12', 'Diciembre')])
    date_year = fields.Char(string="Año", size=4)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        # Data - Jcondori

        lst_account_move_line = self.env['account.invoice'].search([
            ('document_type_id.id', 'like', '2'),
            ('month_year_inv', 'like', self.date_month + "" + self.date_year)
        ])

        content_txt = ""
        estado_ope = ""

        # Iterador - Jcondori
        for line in lst_account_move_line:
            for imp in line.payment_ids:
                if imp.payment_date:
                    estado_ope = imp.payment_date

            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.document_type_id.display_name[0:2] or '',  # 1 jrejas
                line.type_ident or '',  # 2 jrejas
                line.num_ident or '',  # 3 jrejas
                line.document_type_id.name[0:2] or '',  # 4 jrejas
                line.invoice_serie or '',  # 5 jrejas
                line.invoice_number or '',  # 6 jrejas
                line.residual or '',  # 7 jrejas
                line.date_document.strftime("%d/%m/%Y") or '',  # 9 jrejas
                estado_ope.strftime("%d/%m/%Y") or '',  # 10 jrejas          5
                line.amount_tax or '',  # 11 jrejas

            )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "retenciones_4ta.txt"
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'retenciones_4ta',
            'res_model': 'libreria.four_retentions',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
