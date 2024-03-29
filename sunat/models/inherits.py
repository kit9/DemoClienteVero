from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    _inherit = "product.category"

    analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    catalog_id = fields.Many2one('sunat.stock_catalog', 'Catálogo de Stock')
    type_existence_id = fields.Many2one('sunat.type_existence', 'Tipo de Existencia')
    existence_code = fields.Char(string="Código de Existencia")

    tipo_de_act = fields.Selection(string="Cód. Tipo de Act", selection=[
        ('1', '1 NO REVALUADO'),
        ('2', '2 REVALUADO CON EFECTO TRIBUTARIO')
    ])


class ProductProduct(models.Model):
    _inherit = "product.product"

    account_account = fields.Char(string='Cuenta Contable', related="categ_id.property_stock_valuation_account_id.code")


class LandedCost(models.Model):
    _inherit = "stock.landed.cost"

    @api.multi
    def _calculated_cost(self):
        _logger.info("Metodo cabezera")
        for rec in self:
            if rec.state == 'done':
                rec.valuation_adjustment_lines._calculated_cost()


class AdjustmentLines(models.Model):
    _inherit = "stock.valuation.adjustment.lines"

    calculated_cost = fields.Boolean(string='Costo Calculado', default=False)

    @api.multi
    def _calculated_cost(self):
        for rec in self:
            if not rec.calculated_cost:
                account_id = rec.product_id.property_account_expense_id or \
                             rec.product_id.categ_id.property_account_expense_categ_id
                if not account_id:
                    account_id = self.env['account.account'].search([], limit=1)
                total = rec.product_id.qty_available * rec.product_id.standard_price
                total = total + rec.additional_landed_cost
                total = total / rec.product_id.qty_available
                rec.product_id.do_change_standard_price(total, account_id.id)
                rec.calculated_cost = True


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    type_operation_id = fields.Many2one('sunat.type_operation', 'Tipo de Operación')
    document_type_id = fields.Many2one('sunat.document_type', 'Document Type')


class UoM(models.Model):
    _inherit = 'uom.uom'

    sunat_code = fields.Char(string="Código de Sunat", default="99")


class AccountAccount(models.Model):
    _inherit = "account.account"

    target_debit1_id = fields.Many2one('account.account', string='Cuenta de amarre al Debe 1')
    target_debit1_value = fields.Integer(string="Porcentaje 1")

    target_debit2_id = fields.Many2one('account.account', string='Cuenta de amarre al Debe 2')
    target_debit2_value = fields.Integer(string="Porcentaje 2")

    target_debit3_id = fields.Many2one('account.account', string='Cuenta de amarre al Debe 3')
    target_debit3_value = fields.Integer(string="Porcentaje 3")

    target_credit_id = fields.Many2one('account.account', string='Cuenta de amarre al Haber')
    target_account = fields.Boolean(string='Tiene cuenta destino', default=False)

    account_plan_code = fields.Selection(string="Codigo de Plan de Cuenta", selection=[
        ('02 plan contable general revisado', '02 plan contable general revisado'),
    ])


class account_move(models.Model):
    _inherit = 'account.move'

    person_type = fields.Char(string="Inafecto", compute="_person_type")

    invoice_id = fields.Many2one('account.invoice', 'Factura Cliente')

    @api.multi
    @api.depends('partner_id')
    def _person_type(self):
        for rec in self:
            rec.person_type = rec.partner_id.person_type

    def asiento_destino(self):
        accounts = []
        if self.state == "posted":
            for account in self.line_ids:
                if account.account_id.target_account:
                    accounts.append(account)
        if len(accounts) > 0:
            # Lista de Lineas
            lines = []

            for account in accounts:
                # monto
                monto = 0
                if account.debit:
                    monto = account.debit;
                else:
                    if account.credit:
                        monto = account.credit;

                # Linea 4
                lines.append((0, 0, {
                    'account_id': account.account_id.target_credit_id and account.account_id.target_credit_id.id or False,
                    'credit': monto
                }))

                # Linea 3
                if account.account_id.target_debit3_id:
                    lines.append((0, 0, {
                        'account_id': account.account_id.target_debit3_id and account.account_id.target_debit3_id.id or False,
                        'debit': monto * (account.account_id.target_debit3_value / 100)
                    }))

                # Linea 2
                if account.account_id.target_debit2_id:
                    lines.append((0, 0, {
                        'account_id': account.account_id.target_debit2_id and account.account_id.target_debit2_id.id or False,
                        'debit': monto * (account.account_id.target_debit2_value / 100)
                    }))

                # Linea 1
                if account.account_id.target_debit1_id:
                    lines.append((0, 0, {
                        'account_id': account.account_id.target_debit1_id and account.account_id.target_debit1_id.id or False,
                        'debit': monto * (account.account_id.target_debit1_value / 100)
                    }))

            # Asiento
            account_move_dic = {
                'date': str(datetime.now().date()) or False,
                'journal_id': self.journal_id and self.journal_id.id or False,
                'ref': self.ref,
                'line_ids': lines
            }

            account_move = self.env['account.move'].create(account_move_dic)
            account_move.post()


class Partner(models.Model):
    _inherit = 'res.partner'

    detrac_id = fields.Many2one('sunat.detracciones', 'Detraccion')

    document_type_identity_id = fields.Many2one(
        'sunat.document_type_identity', 'Tipo de Documento de Identidad')

    document_num_identity = fields.Char(string="Numero de Documento de Identidad")

    person_type = fields.Selection(string="Tipo de Persona", selection=[('01-Persona Natural', '01-Persona Natural'),
                                                                        ('02-Persona Jurídica', '02-Persona Jurídica'),
                                                                        ('03-Sujeto no Domiciliado',
                                                                         '03-Sujeto no Domiciliado')])
    is_empresa = fields.Boolean(compute="_is_empresa")

    is_employee = fields.Boolean(string='Is a Empleyee', default=False,
                                 help="Check this box if this contact is an Employee.")

    is_withholding_agent = fields.Boolean(string="Agente de Retención")

    # Datos Persona Natural
    ape_pat = fields.Char(string="Apellido Paterno")
    ape_mat = fields.Char(string="Apellido Materno")
    nombres = fields.Char(string="Nombre Completo")

    # Datos Persona Juridica
    age_retencion = fields.Boolean(string="Agente de Retención")
    buen_contribuyente = fields.Boolean(string="Buen Contribuyente")
    age_percepcion = fields.Boolean(string="Agente de Percepción")

    @api.multi
    @api.depends('person_type')
    def _is_empresa(self):
        for rec in self:
            if rec.person_type == '02-Persona Jurídica':
                rec.is_empresa = True
            else:
                rec.is_empresa = False
            # _logger.info("Variable -> " + str(rec.is_empresa))


class res_partner_bank(models.Model):
    _inherit = 'res.partner.bank'

    is_detraction = fields.Boolean(string="Detracción")
    is_retention = fields.Boolean(string="Retención")
    priority = fields.Integer(string="Prioridad")

    account_type = fields.Selection([('C', 'Cuenta Corriente'), ('M', 'Cuenta Maestra'), ],
                                    string='Tipo de Cuenta')
    branch_office = fields.Char(string="Sucursal")


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    asset_id = fields.Many2one('account.asset.asset', 'Activo')

    move_number = fields.Char('Número de Asiento', compute="_move_number")

    @api.multi
    def _move_number(self):
        for rec in self:
            rec.move_number = rec.invoice_id.move_name

    @api.one
    def asset_create(self):
        if self.asset_category_id:
            vals = {
                'name': self.name,
                'code': self.invoice_id.number or False,
                'category_id': self.asset_category_id.id,
                'value': self.price_subtotal_signed,
                'partner_id': self.invoice_id.partner_id.id,
                'company_id': self.invoice_id.company_id.id,
                'currency_id': self.invoice_id.company_currency_id.id,
                'date': self.invoice_id.date_invoice,
                'invoice_id': self.invoice_id.id,
                'first_depreciation_manual_date': str(datetime.now().date()) or False,
                'invoice_line_ids': [(4, self.id)] or False,
            }
            changed_vals = self.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
            vals.update(changed_vals['value'])
            asset = self.env['account.asset.asset'].create(vals)
            # if self.asset_category_id.open_asset:
            #     asset.validate()
        return True


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    employee_id = fields.Many2one('hr.employee', 'Asignado')

    invoice_line_ids = fields.One2many('account.invoice.line', 'asset_id', string='Invoice Lines')

    reason_for_low = fields.Selection(string="Motivo de baja", selection=[('Venta', 'Venta'),
                                                                          ('Deterioro', 'Deterioro')])
    brand = fields.Char(string="Marca")
    model = fields.Char(string="Modelo")
    serie = fields.Char(string="N° Serie")
    active_status = fields.Selection(string="Estado de Activo", selection=[('1', 'Activos en Desuso'),
                                                                           ('2', 'Activos Obsoletos'),
                                                                           ('3', 'Resto de Activos')])

    seat_code = fields.Integer(string="Asiento", related="invoice_id.move_id.id")
    catalog_number = fields.Char(string="Catálogo de stock", related="invoice_line_ids.product_id.catalog_id.number")
    type_existence_id = fields.Integer(string="Tipo de Existencia",
                                       related="invoice_line_ids.product_id.type_existence_id.id")
    product_code = fields.Char(string="Código de Activo",
                               related="invoice_id.invoice_line_ids.product_id.default_code")

    tipo_de_act = fields.Selection(string="Cód. Tipo de Activo.",
                                   related="invoice_id.invoice_line_ids.product_id.tipo_de_act", selection=[
            ('1', '1 NO REVALUADO'),
            ('2', '2 REVALUADO CON EFECTO TRIBUTARIO')
        ])

    existence_code = fields.Char(string="Código De Existencia")

    num_doc = fields.Char(string="Número de documento de autorización para cambiar el método de la depreciación",
                          size=20)

    filter_year = fields.Char(compute="_get_year", store=True, copy=False)

    @api.multi
    @api.depends('date')
    def _get_year(self):
        for rec in self:
            if rec.date:
                rec.filter_year = rec.date.strftime("%Y")

    @api.multi
    @api.depends('invoice_line_ids')
    def update_cost(self):
        for rec in self:
            cost = 0
            for line in rec.invoice_line_ids:
                cost = cost + line.price_subtotal_signed
            rec.value = cost

    @api.multi
    def set_close(self):
        if self.reason_for_low:
            return self.set_to_close()
        else:
            raise ValidationError("Por favor llene el campo Motivo de Baja")
        return True


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # Para filtrar
    month_year_inv = fields.Char(compute="_get_month_invoice", store=True, copy=False)
    filter_year = fields.Char(compute="_get_year", store=True, copy=False)

    @api.multi
    @api.depends('date')
    def _get_month_invoice(self):
        for rec in self:
            if rec.date:
                rec.month_year_inv = rec.date.strftime("%m%Y")

    @api.multi
    @api.depends('date')
    def _get_year(self):
        for rec in self:
            if rec.date:
                rec.filter_year = rec.date.strftime("%Y")

    @api.multi
    def update_ref_invoice(self):
        for rec in self:
            if not rec.ref:
                if rec.invoice_id:
                    rec.ref = rec.invoice_id.name
                if rec.move_id:
                    rec.ref = rec.move_id.name


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # Para filtrar
    month_year_inv = fields.Char(compute="_get_month_invoice", store=True, copy=False)

    @api.multi
    @api.depends('date')
    def _get_month_invoice(self):
        for rec in self:
            if rec.date:
                rec.month_year_inv = rec.date.strftime("%m%Y")


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    seat_name = fields.Char(string="Asiento", related="journal_id.sequence_id.name")
    seat_code = fields.Integer(string="ID Asiento", related="journal_id.sequence_id.id")

    # Usados por la libreria de Pagos Masivos
    back_partner_id = fields.Many2one('res.partner.bank', string='Banco')
    vv_bank = fields.Char(string='Banco', compute="_get_banco")
    number_payment = fields.Integer(string="Numero de Pago Masivo")
    correlative_payment = fields.Integer(string="Numero Correlativo")
    type = fields.Selection([('detraccion', 'Detracción'), ('retencion', 'Retención'), ('factura', 'Factura')],
                            string='Tipo de Pago')

    payment_methods_id = fields.Many2one('sunat.payment_methods', string='Forma de Pago')
    operation_number = fields.Char(string='Número de Operación')

    partner_type = fields.Selection(selection_add=[('is_employee', 'Employee')])

    # Para filtrar
    month_year_inv = fields.Char(compute="_get_month_invoice", store=True, copy=False)

    @api.multi
    @api.depends('payment_date')
    def _get_month_invoice(self):
        for rec in self:
            if rec.payment_date:
                rec.month_year_inv = rec.payment_date.strftime("%m%Y")


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    employee_id = fields.Many2one('hr.employee', string='Empleado')


class Employee(models.Model):
    _inherit = "hr.employee"

    analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica')


class AccountTax(models.Model):
    _inherit = 'account.tax'

    tax_rate = fields.Selection(string="Tipo de Impuesto", selection=[('igv', 'IGV'),
                                                                      ('isc', 'ISC'),
                                                                      ('otros', 'OTROS')])


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    related_invoice_id = fields.Char(string="Factura", related="move_id.invoice_id.number")


class AccountJournal(models.Model):
    _inherit = "account.journal"

    type = fields.Selection(selection_add=[('retention', 'Retención IGV')])

    # 0001 - Incio
    is_detraction = fields.Boolean(string="Es para Detracción")
    # 0001 - Fin


class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    def get_valuation_lines(self):
        lines = []
        _logger.info("Cantidad -> " + str(len(self.mapped('picking_ids').mapped('move_lines'))))
        for move in self.mapped('picking_ids').mapped('move_lines'):
            # it doesn't make sense to make a landed cost for a product that isn't set as being valuated in real time at real cost
            _logger.info("valuation -> " + str(move.product_id.valuation))
            _logger.info("cost_method -> " + str(move.product_id.cost_method))
            _logger.info("if -> " + \
                         str(move.product_id.valuation) + " != real_time or " + str(
                move.product_id.cost_method) + " not in fifo,average")
            if move.product_id.valuation != 'real_time' or move.product_id.cost_method not in 'fifo,average':
                _logger.info("-> continue")
                continue
            vals = {
                'product_id': move.product_id.id,
                'move_id': move.id,
                'quantity': move.product_qty,
                'former_cost': move.value,
                'weight': move.product_id.weight * move.product_qty,
                'volume': move.product_id.volume * move.product_qty
            }
            lines.append(vals)

        _logger.info("lines -> " + str(lines))
        if not lines and self.mapped('picking_ids'):
            raise UserError(_(
                "You cannot apply landed costs on the chosen transfer(s). Landed costs can only be applied for products with automated inventory valuation and FIFO costing method."))
        return lines
