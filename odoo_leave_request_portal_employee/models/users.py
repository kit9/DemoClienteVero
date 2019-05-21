from odoo import models, fields , api

class ResUsers(models.Model):
	_inherit = 'res.users'
	
	portal_employee_leave = fields.Boolean(string='Portal Employee Leave' ,copy = True, default= False)

	# @api.multi
	# def write(self, vals):
	#   res = super(ResUsers, self).write(vals)
	#   if 'portal_employee_leave' in vals:
	#       group = self.env.ref('odoo_leave_request_portal_employee.group_employee_leave')
	#       for rec in self:
	#           if vals['portal_employee_leave'] == True:
	#               group.sudo().write({'users': [(4, rec.id)]})
	#           else:
	#               group.sudo().write({'users': [(3, rec.id)]})
	#   return res

class HrLeave(models.Model):
	_inherit = 'hr.leave'

	def _get_responsible_for_approval(self):
		if self.employee_id.user_id.portal_employee_leave:
			return self.employee_id.user_id
		return super(HrLeave, self)._get_responsible_for_approval()

		