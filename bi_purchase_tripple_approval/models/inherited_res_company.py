# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models

class Company(models.Model):
	_inherit = 'res.company'



	second_approval = fields.Boolean(string="Second Approval" )
	second_approval_minimum_amount = fields.Monetary(srting ="Minimum Amount ")
