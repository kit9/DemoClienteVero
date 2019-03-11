from odoo import models, fields, api
import base64
import logging
import time

_logger = logging.getLogger(__name__)


class chartofaccounts(models.TransientModel):
    _name = "libreria.not_domiciled"
    _description = "No Domiciliados"

    state = fields.Selection(
        [('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.multi
    def generate_file(self):
        # Data - Jcondori

        lst_account_move_line = self.env['account.invoice'].search([])
        content_txt = ""
        # Iterador - Jcondori
        for line in lst_account_move_line:
            # Asiento Conta

            # por cada campo encontrado daran una linea como mostrare
            txt_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s" \
                       "|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (

                           line.date_invoice or '', #1
                           line.move_id.x_studio_field_fwlP9 or '', #2 (Factura/Asiento Contable/ID)
                           line.move_id or '', #3(Factura/Asiento Contable)
                           '', #4
                           '', #5
                           '', #6
                           '', #7
                           '', #8
                           '', #9
                           '', #10
                           '', #11
                           '', #12
                           '', #13
                           '', #14
                           '', #15
                           '', #16
                           '', #17
                           '', #18
                           '', #19
                           '', #20
                           '', #21
                           '', #22
                           '', #23
                           '', #24
                           '', #25
                           '', #26
                           '', #27
                           '', #28
                           '', #29
                           '', #30
                           '', #31
                           '', #32
                           '', #33
                           '', #34
                           '', #35
                           ''  #36

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
