# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	second_approval = fields.Boolean(string="Second Approval" ,related="company_id.second_approval",readonly=False)
	second_approval_minimum_amount = fields.Monetary(srting ="Minimum Amount",related="company_id.second_approval_minimum_amount",readonly=False)

	@api.constrains('second_approval_minimum_amount')
	def warrning_seccond_approval(self) :
		if self.po_order_approval == True and self.second_approval == True :
			if self.po_double_validation_amount > self.second_approval_minimum_amount :
				raise	UserError(_('Second approval amount must be greater than Order approval amount'))