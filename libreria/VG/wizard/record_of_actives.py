from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


###########################################################################################
# -- OPTIMIZA
# -- DESCRIPCION: CLASE HEREDADA DEL STANDAR PARA MODIFICARLO
# -- AUTOR: JOSE LUIS CONDORI JARA
# -- CAMBIOS: ID    FECHA (DD/MM/YYYY)  PERSONA               CAMBIOS EFECTUADOS
# --         #001        --                 --                CREACION DE LA CLASE.
# --         #002       28/05/2019    JOSE CONDORI            CREACION DE LA CLASE.
# -----------------------------------------------------------------------------------------
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
        residual = ""
        res = ""
        rest = ""
        _estado_ope = ""
        value = "linear"
        estado_ope = ""
        _depres = ""
        pxu = ""
        alv = ""
        motivobaja = ""

        # Iterador - Jcondori
        for line in lst_account_move_line:

            # 14
            for imp in line.depreciation_line_ids:
                if imp.sequence == 1:
                    _depres = "%.2f" % imp.remaining_value

            # 16
            for cat2 in line.invoice_line_ids:
                pxu = "%.2f" % sum(line.price_unit for line in
                                   line.invoice_line_ids)  # DATO --- "%.2f" % <-- SE UTILIZA PARA REDONDEAR NUMEROS
                # if cat2.price_unit:
                #     cat2.price_unit
                # if line.category_id.account_asset_id.company_id.id:
                #     rest = line.category_id.account_asset_id.company_id.id

            # 17
            for alv in line.depreciation_line_ids:
                if alv.sequence == 2:
                    motivobaja = "%.2f" % alv.depreciated_value

            # 28
            for cat3 in line.depreciation_line_ids:
                if cat3.sequence == 2:
                    amortizacion = "%.2f" % cat3.depreciated_value

            # 25
            if line.category_id.method == value:
                _estado_ope = "1"
            else:
                _estado_ope = "9"

            # 36
            if line.create_date.strftime("%m%Y") == time.strftime("%m%Y"):
                estado_ope = "1"
            else:
                if line.create_date.strftime("%Y") != time.strftime("%Y"):
                    estado_ope = "8"
                else:
                    if int(time.strftime("%m")) == int(time.strftime("%m")) - 1:
                        estado_ope = "9"
                    else:
                        estado_ope = "1"

            # por cada campo encontrado daran una linea como mostrare
            txt_line = "%s|%s|%s|M%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (

                           line.date.strftime("%Y%m00") or '',  # 1
                           line.invoice_id.move_id.name or '',  # 2
                           line.seat_code or '',  # 3
                           line.seat_code or '',  # 4 cbarraza (crear campo)
                           line.product_code or '',  # 5
                           line.x_studio_cdigo_de_existencia or '',  # 6 cbarraza (crear campo)
                           line.tipo_de_act or '',  # 7
                           line.category_id.account_asset_id.code or '',  # 8
                           line.active_status or '',  # 9
                           line.category_id.name or '',  # 10
                           line.brand or '-',  # 11
                           line.model or '-',  # 12
                           line.serie or '-',  # 13
                           _depres or '',  # 14 (Campo residual)
                           '-',  # 15 null
                           pxu or '',  # 16 ldelacruz (Campo Precio unitario)
                           motivobaja or '',  # 17 ldelacruz (campo motivo de baja)
                           '0.00',  # 18 null
                           '0.00',  # 19 null
                           '0.00',  # 20 null
                           '0.00',  # 21 null
                           '0.00',  # 22 null
                           line.date.strftime("%d/%m/%Y") or '',  # 23
                           line.date.strftime("%d/%m/%Y") or '',  # 24
                           _estado_ope or '',  # 25 jrejas
                           # Inicio #002 Código Original “Comentado”
                           # '',  # 26 null
                           # Fin #001
                           line.num_doc or '',  # 26 - JCondori
                           str("%.2f" % line.category_id.method_number \
                                   if line.category_id.method_number else 0).zfill(6),  # 27
                           amortizacion or '',  # 28
                           '0.00',  # 29 null
                           '0.00',  # 30 null
                           '0.00',  # 31 null
                           '0.00',  # 32 null
                           '0.00',  # 33 null
                           '0.00',  # 34 null
                           '0.00',  # 35 null
                           estado_ope or ''  # 36 jrejas (no se encontro)
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
