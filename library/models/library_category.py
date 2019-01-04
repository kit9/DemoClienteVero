# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LibraryCategory(models.Model):
    _name = 'library.category'

    name = fields.Char(string="Nombre")
    active = fields.Boolean("Esta Activo")
