from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class libromayor(models.TransientModel):
    _name = "libreria.libromayor"
    _description = "libro mayor"


    def _get_periods(self,docs):
        array_period=[]
        for object in docs:
            array_period.append(object.period_id.name)

        periods = list(set(array_period))
        return periods

    def render_html(self,cr,uid,ids,data=None,context=None):
        report_obj = self.pool['libreria']
        report = report_obj.get_report_from_name(
            cr,uid,'libromayor'
        )
        docargs = {

            'doc_ids': ids,
            'doc_model': report.model,
            'docs' : self.pool[report.model].browse(cr,uid,ids,context=context)

        }
        return report_obj.render(cr,uid,ids,'libromayor',docargs,context=context)
