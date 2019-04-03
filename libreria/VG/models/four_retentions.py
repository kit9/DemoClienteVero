# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class retentions(models.Model):
    _inherit = 'account.invoice'

    # Para filtrar
    month_year_move = fields.Char(compute="_get_month_move", store=True, copy=False)

    @api.multi
    @api.depends('create_date')
    def _get_month_move(self):
        for rec in self:
            if rec.create_date:
                rec.month_year_move = rec.create_date.strftime("%m%Y")
