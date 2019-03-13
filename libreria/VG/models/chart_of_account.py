# -*- coding: utf-8 -*-

from odoo import models, fields, api

class chart_of_account(models.Model):
    _name = 'account.account'

    cod_plan_cuenta = fields.Char(string="codigo de cuenta de deudor")

    deudor_tributario = fields.Char(string="Facturación")