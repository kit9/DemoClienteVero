from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class account_10(models.TransientModel):
    _name = "libreria.account_10"
    _description = "account_10"

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

        # modelo a buscar
        dominio = ['&',('month_year_move','like',self.date_month + "" + self.date_year),'|',('dummy_account_id.code', '=', 101001),('dummy_account_id.code', '=', 104001)]

        lst_account_move_line = self.env['account.move'].search(dominio)

        # variables creadas
        content_txt = ""
        campo=""
        campo1 = ""

        # Iterador
        for line in lst_account_move_line:


            # datos a exportar a txt
            txt_line = "%s|%s|%s|%s|%s|%s|%s|" % (
                line.create_date.strftime("%Y%m00") or '',
                line.dummy_account_id.code or '',
                line.journal_id.code or'',
                line.journal_id.bank_account_id.acc_number or'',
                line.currency_id.name or'',
                line.dummy_account_id.opening_debit or '',
                line.dummy_account_id.target_debit3_value or ''
            )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Cuenta_10.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'account_10',
            'res_model': 'libreria.account_10',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }