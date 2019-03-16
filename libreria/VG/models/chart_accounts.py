# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class chartacocounts(models.Model):
    _inherit = 'account.account'

    # Para filtrar
    month_year_inv = fields.Char(compute="_get_month_invoice", store=True, copy=False)

    @api.multi
    @api.depends('create_date')
    def _get_month_invoice(self):
        for rec in self:
            if rec.date:
                rec.month_year_inv = rec.date.strftime("%m%Y")
