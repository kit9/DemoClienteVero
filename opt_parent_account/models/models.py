# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAccount(models.Model):
    _inherit = "account.account"

    parent_account_id = fields.Many2one('account.account', string='Parent Account')
