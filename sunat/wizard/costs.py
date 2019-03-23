from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class InventoryValorized(models.TransientModel):
    # class InventoryValorized(models.Model):
    _name = "sunat.costs"
    _description = "Costos"

    date_year = fields.Char(string="Año", size=4)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    # @api.multi
    def generate_file(self):
        date_year = self.date_year
        filter_year = 0
        if not date_year.isdigit():
            raise ValidationError("No se aceptan estos documentos")
        else:
            filter_year = int(date_year)

        content_txt = ""

        # 2 -> Saldo inicial
        saldo_inicial_2 = 0
        lst_move_line = self.env['account.move.line'].search([
            ('account_id.code', 'like', '20111.01'),
            ('filter_year', 'like', str(filter_year - 1))
        ])

        for line in lst_move_line:
            saldo_inicial_2 = saldo_inicial_2 + (line.debit - line.credit)

        # 3 -> Saldo de Producción
        saldo_inicial_3 = 0
        lst_saldo_ini_3 = self.env['account.move.line'].search([
            # ('account_id.code', 'like', '6211.01'),
            ('account_id.code', 'in', ['6211.01', '241000']),
            ('filter_year', 'like', str(filter_year - 1))
        ])
        for line_i in lst_saldo_ini_3:
            saldo_inicial_3 = saldo_inicial_3 + (line_i.debit - line_i.credit)

        saldo_final_3 = 0
        lst_saldo_fin_3 = self.env['account.move.line'].search([
            # ('account_id.code', 'like', '6211.01'),
            ('account_id.code', 'in', ['6211.01', '241000']),
            ('filter_year', 'like', date_year)
        ])
        for line_f in lst_saldo_fin_3:
            saldo_final_3 = saldo_final_3 + (line_f.debit - line_f.credit)

        saldo_final_3 = saldo_final_3 + saldo_inicial_3
        _logger.info("Costo de Pruduccion")
        _logger.info(saldo_final_3)
        _logger.info(len(lst_saldo_fin_3))

        # 4 -> Saldo Final
        saldo_final_4 = 0
        lst_saldo_fin_4 = self.env['account.move.line'].search([
            ('account_id.code', 'like', '20111.01'),
            ('filter_year', 'like', date_year)
        ])
        for line_4 in lst_saldo_fin_4:
            saldo_final_4 = saldo_final_4 + (line_4.debit - line_4.credit)

        saldo_final_4 = saldo_final_4 + saldo_inicial_2

        content_txt = "%s|%s|%s|%s|%s|%s|%s" % (
            date_year or '',  # 1 -> Periodo
            saldo_inicial_2 or 0.00,  # 2 -> Costo de Inventario Inicial
            saldo_final_3 or '',  # 3 -> Costo de Produccion de Productos
            saldo_final_4,  # 4 -> Costo de Inventario Final
            '',  # 5 -> Ajustes diversos contables
            1,  # 6 -> Indica el estado de la operación
            '',  # 7 -> Campos de libre utilización.
        )

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "costos.txt"
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Reporte de Costos',
            'res_model': 'sunat.costs',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
        # return content_txt
