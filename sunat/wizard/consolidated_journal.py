from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class ConsolidatedJournal(models.TransientModel):
    _name = "sunat.consolidated_journal"
    _description = "Diario Consolidado"

    date_month = fields.Char(string="Mes", size=2)
    date_year = fields.Char(string="Año", size=4)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        dominio = [('move_id.state', 'not like', 'draft'),
                   ('month_year_inv', 'like', self.date_month + "" + self.date_year)
                   ]

        # Data
        lst_account_move_line = self.env['account.move.line'].search(dominio)

        content_txt = ""

        # Iterador
        for line in lst_account_move_line:
            # Asiento Contable

            date_document = ""
            if line.invoice_id.date_document:
                date_document = line.invoice_id.date_document.strftime(
                    "%d/%m/%Y")

            date_invoice = ""
            if line.invoice_id.date_invoice:
                date_invoice = line.invoice_id.date_invoice.strftime(
                    "%d/%m/%Y")

            date_due = ""
            if line.invoice_id.date_due:
                date_due = line.invoice_id.date_due.strftime("%d/%m/%Y")

            name = ""
            if line.invoice_id.number:
                name = line.invoice_id.number.replace("/", "")

            concatenado = ""
            if line.move_id.name:
                concatenado = line.move_id.name
            if line.invoice_id.name:
                if len(concatenado) > 0:
                    concatenado = concatenado + "," + line.invoice_id.name
                else:
                    concatenado = line.invoice_id.name
            if line.ref:
                if len(concatenado) > 0:
                    concatenado = concatenado + "," + line.ref
                else:
                    concatenado = line.ref
            if line.partner_id.name:
                if len(concatenado) > 0:
                    concatenado = concatenado + "," + line.partner_id.name
                else:
                    concatenado = line.partner_id.name

            # 20 -> Tipo
            campo_20 = ""
            if line.journal_id.type == "purchase" and line.partner_id.person_type != "03-Sujeto no Domiciliado":
                campo_20 = "080200"
            if line.journal_id.type == "purchase" and line.partner_id.person_type == "03-Sujeto no Domiciliado":
                campo_20 = "080100"
            if line.journal_id.type == "sale":
                campo_20 = "140100"

            # 21 -> Fechas
            campo_operacion = ''
            if line.invoice_id.date_invoice and line.invoice_id.date_document:
                if line.invoice_id.date_invoice.strftime("%m%Y") == line.invoice_id.date_document.strftime("%m%Y"):
                    campo_operacion = '1'
                else:
                    if line.invoice_id.date_invoice.strftime("%Y") != line.invoice_id.date_document.strftime("%Y"):
                        campo_operacion = '9'
                    else:
                        if int(line.invoice_id.date_invoice.strftime("%m")) == int(
                                line.invoice_id.date_document.strftime("%m")) - 1:
                            campo_operacion = '0'
                        else:
                            campo_operacion = '9'

            txt_line = "%s00|%s|M%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                line.date.strftime("%Y%m") or '',  # -> 01
                name or '',  # -> 02
                line.journal_id.id or '',  # -> 03
                line.account_id.code or '',  # -> 04
                line.company_id.id or '',  # -> 05
                line.analytic_account_id.name or '',  # -> 06
                line.invoice_id.currency_id.name or '',  # -> 07
                line.partner_id.catalog_06_id.code or '',  # -> 08|
                line.partner_id.vat or '',  # -> 09
                line.invoice_id.document_type_id.number or '',  # -> 10
                line.invoice_id.invoice_serie or '',  # -> 11
                line.invoice_id.invoice_number or '',  # -> 12
                date_invoice or '',  # -> 13
                date_due or '',  # -> 14
                date_document or '',  # -> 15
                concatenado or '',  # -> 16
                line.ref or '',  # -> 17
                line.debit or 0.0,  # -> 18
                line.credit or 0.0,  # -> 19
                # line.move_id.name.replace("/", "") or '',  # -> 20
                campo_20 or '',  # -> 20
                campo_operacion or '',  # -> 21
                '' or ''  # -> 22
            )

            # Agregamos la linea al TXT
            content_txt = content_txt + "" + txt_line + "\r\n"

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(content_txt.encode('ISO-8859-1')),
            'txt_filename': "LE2060158712320190200050100001111.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Diario Consolidado',
            'res_model': 'sunat.consolidated_journal',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
