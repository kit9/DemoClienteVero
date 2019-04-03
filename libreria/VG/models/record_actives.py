from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class RecordActives(models.Model):
    _inherit = 'account.asset.asset'

    # Para filtrar
    cod_catalog = fields.Char(compute="_get_cod_catalog", store=True, copy=False)
    cod_asistent = fields.int(compute="_get_cod_asistent", store=True, copy=False)

