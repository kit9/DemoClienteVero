from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class AccountAccount(models.Model):
    _inherit = 'account.account'

    month_year_inv = fields.Char(compute="_get_month_invoice", store=True, copy=False)

    @api.multi
    @api.depends('create_date')
    def _get_month_invoice(self):
        for rec in self:
            if rec.create_date:
                rec.month_year_inv = rec.create_date.strftime("%m%Y")

