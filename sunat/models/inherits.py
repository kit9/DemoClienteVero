from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    catalog_id = fields.Many2one('sunat.stock_catalog', 'Catálogo de Stock')
    type_existence_id = fields.Many2one('sunat.type_existence', 'Tipo de Existencia')
    existence_code = fields.Char(string="Código de Existencia")


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

    def imprimir(self):
        _logger.info("Crear asiento")


class account_move(models.Model):
    _inherit = 'account.move'

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

    @api.multi
    @api.depends('date')
    def _get_month_invoice(self):
        for rec in self:
            if rec.date:
                rec.month_year_inv = rec.date.strftime("%m%Y")

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

    # Usados por la libreria de Pagos Masivos
    back_partner_id = fields.Many2one('res.partner.bank', string='Banco')
    vv_bank = fields.Char(string='Banco', compute="_get_banco")

    # Para filtrar
    month_year_inv = fields.Char(compute="_get_month_invoice", store=True, copy=False)

    @api.multi
    @api.depends('payment_date')
    def _get_month_invoice(self):
        for rec in self:
            if rec.payment_date:
                rec.month_year_inv = rec.payment_date.strftime("%m%Y")
