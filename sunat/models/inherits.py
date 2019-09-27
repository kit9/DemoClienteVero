from passlib.tests.utils import limit

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import logging
import json

_logger = logging.getLogger(__name__)


class IrTranslation(models.Model):
    _inherit = 'ir.translation'

    @api.model
    def _get_import_cursor(self):
        self_ = self.with_context({'overwrite': True})
        return super(IrTranslation, self_)._get_import_cursor()


class ProductCategory(models.Model):
    _inherit = 'product.category'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica')


class UoMCategory(models.Model):
    _inherit = 'uom.category'

    measure_type = fields.Selection(selection_add=[('service', 'Service'),
                                                   ('box', 'Box'),
                                                   ('can', 'Can')])


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    catalog_id = fields.Many2one('sunat.stock_catalog', 'Catálogo de Stock')
    type_existence_id = fields.Many2one('sunat.type_existence', 'Tipo de Existencia')
    existence_code = fields.Char(string='Código de Existencia')
    account_account = fields.Char(string='Accounting Account',
                                  related='categ_id.property_stock_valuation_account_id.code')

    sunat_product_id = fields.Many2one(comodel_name='sunat.product', string='Sunat Product Code', required=True)

    # 0009 - Inicio
    is_imported_product = fields.Boolean(string='Is Imported Product')
    # 0009 - Fin

    tipo_de_act = fields.Selection(string='Cód. Tipo de Act', selection=[
        ('1', '1 NO REVALUADO'),
        ('2', '2 REVALUADO CON EFECTO TRIBUTARIO')
    ])


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # @api.multi
    # def _domain_invoice(self):
    #     _logger.info([('id', 'in', self.sale_id.invoice_ids.ids)])
    #     return [('id', 'in', self.sale_id.invoice_ids.ids)]

    type_operation_id = fields.Many2one('sunat.type_operation', 'Tipo de Operación')
    document_type_id = fields.Many2one('sunat.document_type', 'Document Type')

    # 0009 - Inicio
    invoice_id = fields.Many2one(comodel_name='account.invoice', string='Invoice')
    invoice_ids = fields.Many2many('account.invoice',
                                   compute='_get_sale_invoiced',
                                   string='Invoice', store=True, copy=False)

    # fields.Many2many('account.invoice', string='Invoices', compute='_get_invoiced', readonly=True, copy=False)
    # domain=lambda self: [('id', 'in', self.sale_id.invoice_ids.ids)]

    dua_code = fields.Many2one('sunat.customs_code', 'Dua Code')
    dua_year = fields.Char(string='Dua Year')
    boarding_date = fields.Date(string='Boarding Date')
    dua_serie = fields.Char(string='Dua Serie')
    dua_number = fields.Char(string='Dua Number')

    @api.multi
    @api.depends('sale_id.invoice_ids')
    def _get_sale_invoiced(self):
        for rec in self:
            rec.invoice_ids = rec.sale_id.invoice_ids

    # 0009 - Fin


class UoM(models.Model):
    _inherit = 'uom.uom'

    sunat_code = fields.Char(string='Código de Sunat', default='99')


class AccountAccount(models.Model):
    _inherit = 'account.account'

    target_debit1_id = fields.Many2one('account.account', string='Cuenta de amarre al Debe 1')
    target_debit1_value = fields.Integer(string='Porcentaje 1')

    target_debit2_id = fields.Many2one('account.account', string='Cuenta de amarre al Debe 2')
    target_debit2_value = fields.Integer(string='Porcentaje 2')

    target_debit3_id = fields.Many2one('account.account', string='Cuenta de amarre al Debe 3')
    target_debit3_value = fields.Integer(string='Porcentaje 3')

    target_credit_id = fields.Many2one('account.account', string='Cuenta de amarre al Haber')
    target_account = fields.Boolean(string='Tiene cuenta destino', default=False)

    account_plan_code = fields.Selection(selection=[
        ('02 plan contable general revisado', '02 plan contable general revisado'),
    ], string='Codigo de Plan de Cuenta', default='02 plan contable general revisado')


class AccountMove(models.Model):
    _inherit = 'account.move'

    person_type = fields.Selection(selection=[('01-Persona Natural', '01-Persona Natural'),
                                              ('02-Persona Jurídica', '02-Persona Jurídica'),
                                              ('03-Sujeto no Domiciliado', '03-Sujeto no Domiciliado')],
                                   string='Person Type', related="partner_id.person_type")

    invoice_id = fields.Many2one('account.invoice', 'Factura Cliente')

    def asiento_destino(self):
        accounts = []
        if self.state == 'posted':
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
                    monto = account.debit
                else:
                    if account.credit:
                        monto = account.credit

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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _default_detrac_id(self):
        return self.env['ir.model.data'].xmlid_to_res_id('sunat.sunat_detrac_0')

    detrac_id = fields.Many2one('sunat.detracciones', 'Detraccion', default=_default_detrac_id)

    is_employee = fields.Boolean(string='Is a Empleyee', default=False,
                                 help='Check this box if this contact is an Employee.')

    # 0009 - Inicio
    document_type_identity_id = fields.Many2one('sunat.document_type_identity', 'Tipo de Documento de Identidad')

    document_num_identity = fields.Char(string='Numero de Documento de Identidad')

    is_empresa = fields.Boolean(compute='_is_empresa')

    person_type = fields.Selection(string='Tipo de Persona', selection=[('01-Persona Natural', '01-Persona Natural'),
                                                                        ('02-Persona Jurídica', '02-Persona Jurídica'),
                                                                        ('03-Sujeto no Domiciliado',
                                                                         '03-Sujeto no Domiciliado')])

    # Datos Persona Natural
    ape_pat = fields.Char(string='Apellido Paterno')
    ape_mat = fields.Char(string='Apellido Materno')
    nombres = fields.Char(string='Nombre Completo')

    # Tabla de Personas Juridicas
    sunat_legal_person_id = fields.Many2one('sunat.legal_persons', 'Sunat Persona Juridica')

    # Datos Persona Juridica
    retention_agent = fields.Boolean(string='Agente de Retención', related='sunat_legal_person_id.retention_agent')
    good_contributor = fields.Boolean(string='Buen Contribuyente', related='sunat_legal_person_id.good_contributor')
    perception_agent = fields.Boolean(string='Agente de Percepción', related='sunat_legal_person_id.perception_agent')

    @api.multi
    @api.depends('person_type')
    def _is_empresa(self):
        for rec in self:
            if rec.person_type == '02-Persona Jurídica':
                rec.is_empresa = True
            else:
                rec.is_empresa = False
            # _logger.info('Variable -> ' + str(rec.is_empresa))

    @api.one
    def update_document(self):
        res = super(ResPartner, self).update_document()
        if self.catalog_06_id and str(self.catalog_06_id.code) == '6':
            # if self.vat and len(str(self.vat)) >= 11:
            self.document_type_identity_id = \
                self.env['ir.model.data'].xmlid_to_res_id('sunat.sunat_doc_ident_6') or False
            self.document_num_identity = self.vat
            person = self.env['sunat.legal_persons'].search([('name', '=', self.vat)], order='write_date desc', limit=1)
            self.sunat_legal_person_id = person and person.id or False
            self.person_type = '02-Persona Jurídica'
            if self.response:
                d = json.loads(self.response)
                if d['tipo_documento'] == 'DNI':
                    d = self.get_data_doc_number('dni', d['numero_documento'], format='json')
                    if d['error']:
                        return True
                    d = d['data']
                    part = d.split('|')
                    if len(part[0]) > 0:
                        self.person_type = '01-Persona Natural'
                        self.ape_pat = part[0]
                        self.ape_mat = part[1]
                        self.nombres = part[2]
        else:
            if self.catalog_06_id:
                domain = [('number', '=', self.catalog_06_id.code)]
                ident = self.env['sunat.document_type_identity'].search(domain, limit=1, order='id desc')
                if ident:
                    self.document_type_identity_id = ident and ident.id or False
                    self.document_num_identity = self.vat
                    self.person_type = '03-Sujeto no Domiciliado'
        return res
    # 0009 - Fin


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    is_detraction = fields.Boolean(string='Detracción')
    is_retention = fields.Boolean(string='Retención')
    priority = fields.Integer(string='Prioridad')

    account_type = fields.Selection([('C', 'Cuenta Corriente'), ('M', 'Cuenta Maestra'), ], string='Tipo de Cuenta')
    branch_office = fields.Char(string='Sucursal')


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    asset_id = fields.Many2one('account.asset.asset', 'Activo')
    move_number = fields.Char('Número de Asiento', related='invoice_id.move_name')
    total_discount = fields.Monetary(string='Total Discount', compute='_compute_total_discount', copy=False)
    igv_type = fields.Char(string='IGV type', compute='_compute_igv_type', copy=False)

    @api.one
    def _compute_igv_type(self):
        inafecto = list(filter(lambda line: not line.tax_rate != 'inafecto', self.invoice_line_tax_ids))
        exonerado = list(filter(lambda line: not line.tax_rate != 'exonerado', self.invoice_line_tax_ids))
        if len(inafecto) >= 1:
            self.igv_type = '9'  # Gravado - Operación Onerosa
        elif len(exonerado) >= 1:
            self.igv_type = '8'  # Gravado - Operación Onerosa
        else:
            self.igv_type = '1'  # Gravado - Operación Onerosa

    @api.one
    @api.depends('discount', 'price_unit', 'quantity')
    def _compute_total_discount(self):
        price = self.price_unit * ((self.discount or 0.0) / 100.0)
        discount = self.quantity * price
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            currency = self.invoice_id.currency_id
            date = self.invoice_id._get_currency_rate_date()
            discount = currency._convert(discount,
                                         self.invoice_id.company_id.currency_id,
                                         self.company_id or self.env.user.company_id,
                                         date or fields.Date.today())
        self.total_discount = discount

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

    reason_for_low = fields.Selection(string='Motivo de baja', selection=[('Venta', 'Venta'),
                                                                          ('Deterioro', 'Deterioro')])
    brand = fields.Char(string='Marca')
    model = fields.Char(string='Modelo')
    serie = fields.Char(string='N° Serie')
    active_status = fields.Selection(string='Estado de Activo', selection=[('1', 'Activos en Desuso'),
                                                                           ('2', 'Activos Obsoletos'),
                                                                           ('3', 'Resto de Activos')])

    seat_code = fields.Integer(string='Asiento', related='invoice_id.move_id.id')
    catalog_number = fields.Char(string='Catálogo de stock', related='invoice_line_ids.product_id.catalog_id.number')
    type_existence_id = fields.Integer(string='Tipo de Existencia',
                                       related='invoice_line_ids.product_id.type_existence_id.id')
    product_code = fields.Char(string='Código de Activo',
                               related='invoice_id.invoice_line_ids.product_id.default_code')

    tipo_de_act = fields.Selection(string='Cód. Tipo de Activo.',
                                   related='invoice_id.invoice_line_ids.product_id.tipo_de_act', selection=[
            ('1', '1 NO REVALUADO'),
            ('2', '2 REVALUADO CON EFECTO TRIBUTARIO')
        ])

    existence_code = fields.Char(string='Código De Existencia')

    num_doc = fields.Char(string='Número de documento de autorización para cambiar el método de la depreciación',
                          size=20)

    filter_year = fields.Char(compute='_get_year', store=True, copy=False)

    @api.multi
    @api.depends('date')
    def _get_year(self):
        for rec in self:
            if rec.date:
                rec.filter_year = rec.date.strftime('%Y')

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
            raise ValidationError('Por favor llene el campo Motivo de Baja')
        return True


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Para filtrar
    month_year_inv = fields.Char(compute='_get_month_invoice', store=True, copy=False)
    filter_year = fields.Char(compute='_get_year', store=True, copy=False)

    @api.multi
    @api.depends('date')
    def _get_month_invoice(self):
        for rec in self:
            if rec.date:
                rec.month_year_inv = rec.date.strftime('%m%Y')

    @api.multi
    @api.depends('date')
    def _get_year(self):
        for rec in self:
            if rec.date:
                rec.filter_year = rec.date.strftime('%Y')

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
    month_year_inv = fields.Char(compute='_get_month_invoice', store=True, copy=False)

    @api.multi
    @api.depends('date')
    def _get_month_invoice(self):
        for rec in self:
            if rec.date:
                rec.month_year_inv = rec.date.strftime('%m%Y')


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    seat_name = fields.Char(string='Asiento', related='journal_id.sequence_id.name')
    seat_code = fields.Integer(string='ID Asiento', related='journal_id.sequence_id.id')

    # Usados por la libreria de Pagos Masivos
    back_partner_id = fields.Many2one('res.partner.bank', string='Banco')
    vv_bank = fields.Char(string='Banco', compute='_get_banco')
    number_payment = fields.Integer(string='Numero de Pago Masivo')
    correlative_payment = fields.Integer(string='Numero Correlativo')
    type = fields.Selection([('detraccion', 'Detracción'), ('retencion', 'Retención'), ('factura', 'Factura')],
                            string='Tipo de Pago')

    payment_methods_id = fields.Many2one('sunat.payment_methods', string='Forma de Pago')
    operation_number = fields.Char(string='Número de Operación')

    partner_type = fields.Selection(selection_add=[('is_employee', 'Employee')])

    # Para filtrar
    month_year_inv = fields.Char(compute='_get_month_invoice', store=True, copy=False)

    @api.multi
    @api.depends('payment_date')
    def _get_month_invoice(self):
        for rec in self:
            if rec.payment_date:
                rec.month_year_inv = rec.payment_date.strftime('%m%Y')

    @api.multi
    @api.depends('back_partner_id')
    def _get_banco(self):
        for rec in self:
            if rec.back_partner_id:
                rec.vv_bank = rec.back_partner_id.bank_id.name + ' ' + rec.back_partner_id.acc_number or ''


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    employee_id = fields.Many2one('hr.employee', string='Empleado')


class Employee(models.Model):
    _inherit = 'hr.employee'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica')


class AccountTax(models.Model):
    _inherit = 'account.tax'

    tax_rate = fields.Selection(selection=[('none', 'Ninguno'),
                                           ('igv', 'IGV'),
                                           ('isc', 'ISC'),
                                           ('exonerado', 'Exonerado'),
                                           ('inafecto', 'Inafecto'),
                                           ('no_gravado', 'No Gravado'),
                                           ('otros', 'Otros')],
                                string='Tipo de Impuesto', default='none', required=True)

    @api.multi
    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None):
        res = super(AccountTax, self).compute_all(price_unit, currency, quantity, product, partner)
        taxes = []
        for tax in res['taxes']:
            tax_ = tax
            _tax = self.env['account.tax'].browse(tax['id'])
            tax_['type'] = _tax.tax_rate
            taxes.append(tax)
        res['taxes'] = taxes
        return res


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    related_invoice_id = fields.Char(string='Factura', related='move_id.invoice_id.number')


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    type = fields.Selection(selection_add=[('retention', 'Retención IGV')])

    sunat_serie_id = fields.Many2one(comodel_name='sunat.series', string='Serie', ondelete="restrict")

    # 0001 - Incio
    is_detraction = fields.Boolean(string='Detracción')
    # 0001 - Fin

    # 0010 - Inicio
    is_anticipo = fields.Boolean(string='Anticipo')
    # 0010 - Fin
