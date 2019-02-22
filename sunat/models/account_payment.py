from odoo import models, fields, api, osv
import logging

_logger = logging.getLogger(__name__)


class account_payment(models.Model):
    _inherit = 'account.payment'

    def demo_action(self, cr, uid, ids, context=None):
        _logger.info("Accion ejecutada")
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': 'http://localhost:8069/excel/1',
        #     'nodestroy': True,
        #     'target': 'new'
        # }
        return {
            # 'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'nodestroy': True,
            'target': 'new',
            'url': 'http://localhost:8069/excel/1'
        }
        # return True
