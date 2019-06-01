from odoo import models, fields , api

class MailChannel(models.Model):
    _inherit = 'mail.channel'

    @api.model
    def create(self, vals):
        if self.env.user.has_group("base.group_portal") and self.env.user.portal_employee_leave:
            return super(MailChannel, self).create(vals)
        elif self.env.user.has_group("base.group_portal") and not self.env.user.portal_employee_leave:
            return True
        return super(MailChannel, self).create(vals)
