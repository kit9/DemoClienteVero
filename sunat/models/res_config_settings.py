from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Company(models.Model):
    _inherit = 'res.company'

    electronic_invoicing = fields.Boolean(string="Electronic Invoicing Peru")
    api_token = fields.Char(string="NubeFact API Token")
    api_url = fields.Char(string="NubeFact API URL")

    # 0009 - Inicio
    legal_representative = fields.Many2one(comodel_name="hr.employee", string="Legal Representative", required=True)
    # 0009 - Fin


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    electronic_invoicing = fields.Boolean(string="Electronic Invoicing Peru",
                                          related="company_id.electronic_invoicing",
                                          readonly=False)
    api_token = fields.Char(string="NubeFact API Token",
                            related="company_id.api_token",
                            readonly=False)
    api_url = fields.Char(string="NubeFact API URL",
                          related="company_id.api_url",
                          readonly=False)
