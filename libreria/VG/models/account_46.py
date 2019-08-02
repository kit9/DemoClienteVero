from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class account_46(models.Model):
    _inherit = 'account.move.line'

    # Para filtrar
    year_move_line = fields.Char(compute="_get_month_move", store=True, copy=False)

    @api.multi
    @api.depends('create_date')
    def _get_month_move(self):
        for rec in self:
            if rec.create_date:
                rec.year_move_line = rec.create_date.strftime("%Y")
