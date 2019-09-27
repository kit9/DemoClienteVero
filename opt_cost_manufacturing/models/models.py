from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import json
import logging

_logger = logging.getLogger(__name__)


class MrpCostStructure(models.AbstractModel):
    _inherit = 'report.mrp_account.mrp_cost_structure'

    @api.multi
    def get_lines(self, productions):
        res = super(MrpCostStructure, self).get_lines(productions)
        new_res = []
        for rec in res:
            line = rec
            overheads = []
            labours = []
            for _line in productions.pro_overhead_cost_ids:
                overheads.append(_line)
            for labour in productions.pro_labour_cost_ids:
                labours.append(labour)
            line['overheads'] = overheads
            line['labours'] = labours
            new_res.append(line)
        _logger.info(new_res)
        return new_res


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # Para filtrar
    month_year_inv = fields.Char(compute="_get_month_invoice", store=True, copy=False)

    general_cost_id = fields.Many2one("mrp.general_cost", string="General Cost")

    @api.multi
    @api.depends('date_planned_start')
    def _get_month_invoice(self):
        for rec in self:
            if rec.date_planned_start:
                rec.month_year_inv = rec.date_planned_start.strftime("%m%Y")


class MrpBomLabourCost(models.Model):
    _inherit = "mrp.bom.labour.cost"
    general_cost_id = fields.Many2one("mrp.general_cost", string="General Cost")


class MrpBomOverheadCost(models.Model):
    _inherit = "mrp.bom.overhead.cost"

    general_cost_id = fields.Many2one("mrp.general_cost", string="General Cost")


class GeneralCost(models.Model):
    _name = "mrp.general_cost"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "General Cost"

    name = fields.Text(string="Nombre", compute="_compute_name", store=True, copy=False)
    state = fields.Selection([('pending', 'Pending'),
                              ('complete', 'Complete')],
                             string='Status', default='pending', copy=False,
                             track_visibility='onchange')
    period_year = fields.Char(string="Period Year", required=True, track_visibility='onchange')
    type = fields.Selection(selection=[('1', 'Manufacturing Overhead Cost'),
                                       ('2', 'Direct Labour Cost')],
                            string="Type", required=True, track_visibility='onchange')
    period_month = fields.Selection(selection=[('01', 'January'),
                                               ('02', 'February'),
                                               ('03', 'March'),
                                               ('04', 'April'),
                                               ('05', 'May'),
                                               ('06', 'June'),
                                               ('07', 'July'),
                                               ('08', 'August'),
                                               ('09', 'September'),
                                               ('10', 'October'),
                                               ('11', 'November'),
                                               ('12', 'December')],
                                    string="Period Month", required=True, track_visibility='onchange')
    operation_id = fields.Many2one('mrp.routing.workcenter', string="Operation", track_visibility='onchange')
    product_id = fields.Many2one('product.template', string="Product", track_visibility='onchange')
    # planned_qty = fields.Float(string="Planned Qty", default=0.0,
    #                            )
    # actual_qty = fields.Float(string="Actual Qty", default=0.0,
    #                           )
    uom_id = fields.Many2one('uom.uom', string="UOM")
    # cost = fields.Float(string="Cost/Unit",
    #                     )

    production_ids = fields.One2many('mrp.production', 'general_cost_id', string='Production Orders', copy=False)

    total_cost = fields.Float(string="Amount Total", required=True)

    @api.constrains('period_year', 'period_month')
    def _check_durations(self):
        current_year = int(datetime.now().year)
        current_month = int(datetime.now().month)
        # if int(self.period_month) > current_month:
        #     raise ValidationError("El mes seleccionado no puede ser mayor")
        if int(self.period_month) < (current_month - 1) or int(self.period_month) > current_month:
            raise ValidationError("Solo puede seleccionar el mes actual o anterior")
        if int(self.period_year) < (current_year - 1) or int(self.period_year) > current_year:
            raise ValidationError("Solo puede seleccionar el año actual o anterior")

    @api.multi
    @api.depends('period_year', 'period_month')
    def _compute_name(self):
        for rec in self:
            rec.name = "%s-%s" % (rec.period_year or '', rec.period_month or '')

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        res = {}
        if not self.product_id:
            return res
        self.uom_id = self.product_id.uom_id.id

    @api.multi
    def action_process_overhead(self):
        for rec in self:
            if rec.state == 'pending':
                order_obj = self.env['mrp.production']
                overhead_obj = self.env['mrp.bom.overhead.cost']
                labour_obj = self.env['mrp.bom.labour.cost']
                orders = order_obj.search([('state', '=', 'done'),
                                           ('month_year_inv', 'like', rec.period_month + rec.period_year)])
                if rec.total_cost <= 0:
                    raise ValidationError("Tiene que ingresar el importe")
                if len(orders) <= 0:
                    raise ValidationError("No se encontraron Ordenes de Producción hechos")
                unit_cost = rec.total_cost / len(orders)
                validate = True
                for line in orders:
                    line.general_cost_id = rec
                    list = []
                    if rec.type == '1':
                        list_exis = line.pro_overhead_cost_ids
                    else:
                        list_exis = line.pro_labour_cost_ids
                    for item in list_exis:
                        if item.general_cost_id == rec:
                            list.append(item)
                    if len(list) <= 0:
                        overhead_dic = {
                            'operation_id': rec.operation_id and rec.operation_id.id or False,
                            'product_id': rec.product_id and rec.product_id.id or False,
                            'planned_qty': 1,
                            'actual_qty': 1,
                            'uom_id': rec.uom_id and rec.uom_id.id or False,
                            'cost': unit_cost or 0,
                            'general_cost_id': rec and rec.id or False,
                        }
                        if rec.type == '1':
                            overhead_dic['mrp_pro_overhead_id'] = line and line.id or False
                            overhead = overhead_obj.create(overhead_dic)
                        else:
                            overhead_dic['mrp_pro_labour_id'] = line and line.id or False
                            overhead = labour_obj.create(overhead_dic)
                        if not overhead:
                            validate = False
                if validate:
                    rec.state = 'complete'
                else:
                    raise ValidationError("Hubo un error en el proceso")
