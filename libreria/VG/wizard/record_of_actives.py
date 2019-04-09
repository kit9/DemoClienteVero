from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class RecordActives(models.TransientModel):
    _name = "libreria.record_of_actives"
    _description = "Registro de Activos"

    date_year = fields.Char(string="Año", size=4)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        # Data - Jcondori

        lst_account_move_line = self.env['account.asset.asset'].search([('filter_year', 'like', self.date_year)])
        content_txt = ""
        valor = ""
        residual = ""
        res = ""
        v1 = ""
        _depre = ""
        _estado_ope = ""
        value = "linear"
        estado_ope = ""

        # Iterador - Jcondori
        for line in lst_account_move_line:

            for imp in line.depreciation_line_ids:
                if imp.remaining_value:
                    _depre = imp.remaining_value

            # Asiento Conta
            for cat1 in line.depreciation_line_ids:
                if cat1.depreciated_value:
                    valor = cat1.depreciated_value
            for cat0 in line.depreciation_line_ids:
                if cat0.remaining_value:
                    residual = cat0.remaining_value
            for cat2 in line.invoice_line_ids:
                if cat2.price_unit:
                    res = cat2.price_unit
                if line.category_id.account_asset_id.company_id.id:
                    v1 = line.category_id.account_asset_id.company_id.id

            for cat3 in line.depreciation_line_ids:
                if cat3.depreciated_value:
                    amortizacion = cat3.depreciated_value

            if line.category_id.method == value:
                _estado_ope = "01"
            else:
                _estado_ope = "09"

            if line.create_date.strftime("%m%Y") == time.strftime("%m%Y"):
                estado_ope = "01"
            else:
                if line.create_date.strftime("%Y") != time.strftime("%Y"):
                    estado_ope = "08"
                else:
                    if int(time.strftime("%m")) == int(time.strftime("%m")) - 1:
                        estado_ope = "09"
                    else:
                        estado_ope = "01"

            # por cada campo encontrado daran una linea como mostrare
            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (

                           line.date.strftime("%Y%m00") or '',  # 1
                           line.invoice_id.move_id.name or '',  # 2
                           line.invoice_id.move_id.name or '',  # 3
                           '',  # 4 cbarraza (crear campo)
                           line.name or '',  # 5
                           '',  # 6 cbarraza (crear campo)
                           line.name or '',  # 7
                           line.category_id.account_asset_id.code or '',  # 8
                           line.entry_count or '',  # 9
                           line.category_id.name or '',  # 10
                           line.brand or '',  # 11
                           line.model or '',  # 12
                           line.serie or '',  # 13
                           _depre or '',  # 14 (Campo residual)
                           '',  # 15 null
                           res or '',  # 16 ldelacruz (Campo Precio unitario)
                           line.reason_for_low or '',  # 17 ldelacruz (campo motivo de baja)
                           '',  # 18 null
                           '',  # 19 null
                           '',  # 20 null
                           '',  # 21 null
                           '',  # 22 null
                           line.date.strftime("%d/%m/%Y") or '',  # 23
                           line.date.strftime("%d/%m/%Y") or '',  # 24
                           _estado_ope or '',  # 25 jrejas
                           '',  # 26 null
                           line.category_id.method_number or '',  # 27
                           amortizacion or '',  # 28
                           '',  # 29 null
                           '',  # 30 null
                           '',  # 31 null
                           '',  # 32 null
                           '',  # 33 null
                           '',  # 34 null
                           '',  # 35 null
                           estado_ope or '',  # 36 jrejas (no se encontro)
                           line.value_residual or ''
                       )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "Registro_Activos.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Registro de Activos',
            'res_model': 'libreria.record_of_actives',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }