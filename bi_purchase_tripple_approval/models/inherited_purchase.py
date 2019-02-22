# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	state = fields.Selection([
			('draft', 'RFQ'),
			('sent', 'RFQ Sent'),
			('to approve', 'To Approve'),
			('to second approval','To Second Approval'),
			('purchase', 'Purchase Order'),
			('done', 'Locked'),
			('cancel', 'Cancelled')
		], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')



	@api.multi
	def button_confirm(self):
		res = self.env['res.config.settings'].sudo().search([], order="id desc", limit=1)
		for order in self:
			if order.state not in ['draft', 'sent']:
				continue
			order._add_supplier_to_product()
			# Deal with double validation process
			if order.company_id.po_double_validation == 'one_step'\
					or (order.company_id.po_double_validation == 'two_step'\
						and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
					or order.user_has_groups('purchase.group_purchase_manager'):
				order.button_approve()
			else:
				order.write({'state': 'to approve'})

			if res.po_order_approval == True and order.amount_total > res.po_double_validation_amount :
				order.write({'state': 'to approve'})

				



		return True
 



	@api.multi
	def button_approve(self, force=False):
		res = self.env['res.config.settings'].sudo().search([], order="id desc", limit=1)


		if res.second_approval == True and self.amount_total > res.second_approval_minimum_amount :
			self.write({'state' :'to second approval'})
		else :			
			self.write({'state': 'purchase', 'date_approve': fields.Date.context_today(self)})
			self._create_picking()
			self.filtered(
				lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
		return {}

	@api.multi
	def button_second_approve(self):
		for order in self :
			order.write({'state':'purchase','date_approve': fields.Date.context_today(self)})
