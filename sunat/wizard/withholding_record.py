from xml import dom

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from io import BytesIO
import xlsxwriter
import base64
import logging

_logger = logging.getLogger(__name__)


class withholding_record_export(models.TransientModel):
    _name = "withholding.record"
    _description = "Export Excel"

    date_month = fields.Char(string="Mes", size=2)
    date_year = fields.Char(string="Año", size=4)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):

        dominio = [('type', 'like', 'retencion'),
                   ('month_year_inv', 'like', self.date_month + "" + self.date_year)]

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # Data
        # lst_payments = self.env['account.payment'].search([])
        lst_payments = self.env['account.payment'].search(dominio)

        # Start from the first cell. Rows and columns are zero indexed.
        row = 0
        col = 0

        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': 1})

        border = workbook.add_format({'text_wrap': 1, 'border': 1})

        worksheet.merge_range("A1:A3", "FECHA DE PAGO O RETENCIÓN", merge_format)
        worksheet.merge_range("E1:G1", "MONTO DE LA RETRIBUCIÓN", merge_format)
        worksheet.write("A4", "(dd/mm/aaaa)",merge_format)
        worksheet.merge_range(
            "B1:D1", "PERSONA QUE BRINDÓ EL SERVICIO", merge_format)

        worksheet.merge_range("B2:B4", "TIPO DE DOCUMENTO", merge_format)
        worksheet.merge_range("C2:C4", "N° DE DOCUMENTO", merge_format)
        worksheet.merge_range("D2:D4", "RAZON SOCIAL", merge_format)
        worksheet.merge_range("E2:E4", "MONTO BRUTO", merge_format)
        worksheet.merge_range("F2:F4", "RETENCIÓN EFECTUADA", merge_format)
        worksheet.merge_range("G2:G4", "MONTO NETO", merge_format)

        row += 4

        # worksheet.set_row(0, 35, border)
        worksheet.set_column('A:A', 15)
        worksheet.set_column('D:D', 30)

        # Iterador
        for payment in lst_payments:
            # fecha
            fecha = ''
            if payment.payment_date:
                fecha = payment.payment_date.strftime("%d/%m/%Y")

            for invoice in payment.invoice_ids:
                worksheet.write(row, col, fecha)
                worksheet.write(row, col + 1, invoice.partner_id.catalog_06_id.name or '')
                worksheet.write(row, col + 2, invoice.partner_id.vat or '')
                worksheet.write(row, col + 3, invoice.partner_id.name or '')
                worksheet.write(row, col + 4, invoice.amount_total or 0)
                worksheet.write(row, col + 5, payment.amount or 0)
                worksheet.write(row, col + 6, invoice.amount_total - payment.amount or 0)
                # worksheet.write(row, col + 7, payment.type or '')
                row += 1

        workbook.close()
        output.seek(0)

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(output.getvalue()),
            'txt_filename': "retenciones.xlsx"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Export Excel',
            'res_model': 'withholding.record',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
