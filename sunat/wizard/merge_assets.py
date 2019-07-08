from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ConsolidatedJournal(models.TransientModel):
    _name = "sunat.merge_assets"
    _description = "Fusionar Activos"

    asset_id = fields.Many2one('account.asset.asset', 'Activo', domain="[('state','not like','draft')]")

    @api.model
    def default_get(self, fields):
        assets = super(ConsolidatedJournal, self).default_get(fields)
        assets_cxt_ids = self._context.get('active_ids')
        assets_ids = self.env['account.asset.asset'].browse(assets_cxt_ids)
        for asset in assets_ids:
            if asset.state != 'draft':
                raise ValidationError('Solo activos en borrador')
        return assets

    @api.multi
    def merge_assets(self):
        assets_cxt_ids = self._context.get('active_ids')
        assets_ids = self.env['account.asset.asset'].browse(assets_cxt_ids)
        for asset in assets_ids:
            if len(asset.invoice_line_ids) > 0:
                self.asset_id.write({
                    'invoice_line_ids': [(4, asset.invoice_line_ids[0].id)] or False
                })
            asset.unlink()
        self.asset_id.update_cost()

        return True
