# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ChartAccount(models.Model):
    _inherit = 'account.asset.asset'

    Cod_Catalog = fields.Char(compute="_compute_cod_catalog", store=True, copy=False)
    Cod_Existent = fields.Char(compute="_compute_cod_existent", store=True, copy=False)
