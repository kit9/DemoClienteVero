from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import logging

_logger = logging.getLogger(__name__)


class AccountInvoiceConfirm(models.TransientModel):
    _name = "account.invoice.txt"
    _description = "Generate TXT"

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)
    txt_content = fields.Text()

    @api.multi
    def generate_file(self):
        inv_ids = self._context.get('active_ids')
        invoice_ids = self.env['account.invoice'].browse(inv_ids)
        content = ""
        for inv in invoice_ids:
            content = content + "" + inv._generate_txt_content() + "\n"
        self.write({
            'state': 'get',
            'txt_binary': base64.encodestring(content.encode('ISO-8859-1')),
            'txt_filename': "compras.txt"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generar TXT',
            'res_model': 'account.invoice.txt',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
