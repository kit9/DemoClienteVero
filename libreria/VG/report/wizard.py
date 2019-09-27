from odoo import models, fields, api


class Wizard(models.AbstractModel):
    _name = 'libreria.wizard'
    product_id = fields.Many2one('product.product', string='Producto', widget='selection', store=False)

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('velfasa.utilities')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self.product_id,
        }
        return report_obj.render('libreria.utilities', docargs)
