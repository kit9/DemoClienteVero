from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


###########################################################################################
# -- OPTIMIZA
# -- DESCRIPCION: CLASE HEREDADA DEL STANDAR PARA MODIFICARLO
# -- AUTOR: JOSE LUIS CONDORI JARA
# -- CAMBIOS: ID     FECHA (DD/MM/YYYY)  PERSONA               CAMBIOS EFECTUADOS
# --          #001   23/05/2019          JOSE CONDORI          CREACION DE LA CLASE.
# --          #002   25/05/2019          JOSE CONDORI          AGREGAR CODIGO
# -----------------------------------------------------------------------------------------
class AccountAccount(models.Model):
    _inherit = 'account.account'

    # Para filtrar
    month_year_inv = fields.Char(compute="_get_month_invoice", store=True, copy=False)

    # Inicio #002 "Original"
    # campo_nuevo = fields.Char(compute="_get_month_invoice", store=True, copy=False)
    # Fin #0002
    #-campo_nuevo = fields.Char(compute="_get_month_invoice")

    @api.multi
    @api.depends('create_date')
    def _get_month_invoice(self):
        for rec in self:
            if rec.create_date:
                rec.month_year_inv = rec.create_date.strftime("%m%Y")

    # Inicio #002 "Eliminado"
    #@api.multi
    #@api.depends('create_date')
    #def _get_month_invoice(self):
    #    for rec in self:
    #        if rec.create_date:
    #            rec.month_year_inv = rec.create_date.strftime("%m%Y")
    # Fin #0002


class Invoice(models.Model):
    _inherit = 'account.invoice'

    date_vg = fields.Date(string="Fecha de Valle Grande", readonly=True, required=True, copy=False)
