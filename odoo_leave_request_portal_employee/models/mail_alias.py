from odoo import models, fields , api

class MailAlias(models.Model):
    _inherit = 'mail.alias'

    @api.model
    def create(self, vals):
        if self.env.user.has_group("base.group_portal") and self.env.user.portal_employee_leave:
            return super(MailAlias, self).create(vals)
        elif self.env.user.has_group("base.group_portal") and not self.env.user.portal_employee_leave:
            return True
        return super(MailAlias, self).create(vals)
