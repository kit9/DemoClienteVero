from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class chartofaccounts(models.TransientModel):
    _name = "libreria.chart_accounts"
    _description = "Plan Contable"

    date_month = fields.Char(string="Mes", size=2)
    date_year = fields.Char(string="Año", size=4)

    state = fields.Selection(
        [('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        dominio = [('create_date', 'like', self.date_month + "" + self.date_year)]
        # Data - Jcondori
        # lst_account_move_line = self.env['account.move.line'].search([])
        lst_account_move_line = self.env['account.account'].search(dominio)

        content_txt = ""
        estado_ope = ""

        # Iterador - Jcondori
        for line in lst_account_move_line:

            if line.create_date.strftime("%m%Y") == time.strftime("%m%Y"):
                estado_ope = "01"
            else:
                if line.create_date.strftime("%Y") != time.strftime("%Y"):
                    estado_ope = "09"
                else:
                    if int(time.strftime("%m")) == int(line.date.strftime("%m")) - 1:
                        estado_ope = "00"
                    else:
                        estado_ope = "09"

            # Asiento Conta

            txt_line = "%s|%s|%s|%s|%s|%s" % (
                line.create_date.strftime("%Y%m00") or '|',
                line.code or '|',
                line.name or '|',
                '|',#line.x_studio_codigo_plan_cuenta or ''
                '|',#line.x_studio_deudor_tributario or ''
                estado_ope or '|'

            )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "plan_contable.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Plan Contable',
            'res_model': 'libreria.chart_accounts',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
