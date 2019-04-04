# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging


_logger = logging.getLogger(__name__)


class RecordOfActives(models.Model):
    _inherit = 'account.asset.asset'

    Cod_Catalog = fields.Char(string="Codigo de catalogo")
    Cod_Existent = fields.Char(string="Codigo de Existencia")
