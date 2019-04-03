from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class chart_account(models.TransientModel):
    _name = "VG.wizard.chart_account"
    _description = "Plan Contable"

    date_month = fields.Char(string="Mes", size=2)
    date_year = fields.Char(string="Año", size=4)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        # filtro de fecha
        dominio = [('month_year_inv', 'like', self.date_month + "" + self.date_year)]

        # modelo a buscar
        lst_account_move_line = self.env['account.account'].search(dominio)

        # variables creadas
        content_txt = ""
        estado_ope = ""
        campo = ""
        campo1 = ""

        # Iterador
        for line in lst_account_move_line:
            # validador de estado de operación
            if line.create_date.strftime("%m%Y") == time.strftime("%m%Y"):
                estado_ope = "01"
            else:
                if line.create_date.strftime("%Y") != time.strftime("%Y"):
                    estado_ope = "09"
                else:
                    if int(time.strftime("%m")) == int(time.strftime("%m")) - 1:
                        estado_ope = "00"
                    else:
                        estado_ope = "09"
            # validador de campo vacio
            if line.account_plan_code:
                campo = line.account_plan_code
            if line.account_plan_code:
                campo1 = line.account_plan_code

            # datos a exportar a txt

            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.create_date.strftime("%Y%m00") or '',  # Periodo
                line.code or '',  # codigo cuenta contable
                line.name or '',  # descripcion de cuenta
                campo[0:2] or '',  # Codigo Plan de Cuenta
                campo1[2:50] or '',  # Descripcion del plan de cuenta
                '',  # dejar en blanco
                '',  # dejar en blanco
                estado_ope or ''  # estado de operacion

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
            'res_model': 'VG.wizard.chart_account',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
