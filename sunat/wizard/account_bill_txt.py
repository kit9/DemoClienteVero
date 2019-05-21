from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import logging

_logger = logging.getLogger(__name__)


class AccountInvoiceConfirm(models.TransientModel):
    _name = "account.bill.txt"
    _description = "Generate TXT"

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    # Parametros
    date_month = fields.Char(string="Mes", size=2)
    date_year = fields.Char(string="Año", size=4)
    type = fields.Selection(string="Factura de", selection=[('out_invoice', 'Clientes'), ('in_invoice', 'Proveedores')])
    company_id = fields.Many2one('res.company', string='Compañia')

    @api.multi
    def generate_file(self):

        type_doc = ""
        if self.type == "out_invoice":
            type_doc = ['out_invoice', 'out_refund']
        elif self.type == "in_invoice":
            type_doc = ['in_invoice']
        else:
            raise ValidationError("No se encontraton facturas")

        dominio = [('type', 'in', type_doc),
                   ('state', 'not like', 'draft'),
                   ('month_year_inv', 'like', self.date_month + "" + self.date_year),
                   ('company_id', '=', self.company_id.id)]

        invoice_ids = self.env['account.invoice'].search(dominio, order="id asc")

        if len(invoice_ids) == 0:
            raise ValidationError("No se encontraton facturas")

        content = ""
        if self.type == "in_invoice":
            for inv in invoice_ids:
                content = content + "" + inv._generate_txt_bill() + "\r\n"
            self.write({
                'state': 'get',
                'txt_binary': base64.encodestring(content.encode('ISO-8859-1')),
                'txt_filename': "compras.txt"
            })
        if self.type == "out_invoice":
            for inv in invoice_ids:
                content = content + "" + inv._generate_txt_invoice() + "\r\n"
            self.write({
                'state': 'get',
                'txt_binary': base64.encodestring(content.encode('ISO-8859-1')),
                'txt_filename': "ventas.txt"
            })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generar TXT',
            'res_model': 'account.bill.txt',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
