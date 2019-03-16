from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class AccountAccount(models.Model):
    _inherit = 'account.account'

    # Para filtrar
    month_year_inv = fields.Char(compute="_get_month_invoice", store=True, copy=False)

    @api.multi
    @api.depends('date')
    def _get_month_invoice(self):
        for rec in self:
            if rec.date:
                rec.month_year_inv = rec.date.strftime("%m%Y")
