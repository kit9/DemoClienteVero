# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    portal_employee_expense = fields.Boolean(string='Portal Employee Expense', copy=True, default=False)


class HrExpense(models.Model):
    _inherit = "hr.expense"

    fec_hor_viaje = fields.Datetime(string="Fecha/Hora de Inicio de Viaje", default=fields.Datetime.now)
    fec_viaje = fields.Date(string="Fecha de Viaje", default=fields.Date.context_today)
    hor_ini_viaje = fields.Char(string="Hora Inicio de Viaje")
    centro_costo = fields.Char(string="Centro de Costo")
    cc_variable = fields.Char(string="CC Variable")
    solid_por = fields.Char(string="Solicitado por")
    id_emp_sol = fields.Char(string="Cod. Empleado Solicitante")
    divisa = fields.Char(string="Divisa")
    precio_total = fields.Char(string="Precio Total tras descuento")
    nom_pasajero = fields.Char(string="Pasajero (Nombre del Pasajero)")
    id_pasajero = fields.Char(string="Cod. Empleado Pasajero")
    email_pasajero = fields.Char(string="Email del pasajero")
    model_vehiculo = fields.Char(string="Modelo de Vehículo")
    punto_salida = fields.Char(string="Punto de Salida")
    punto_destino = fields.Char(string="Punto de Destino")
    tipo_peticion = fields.Char(string="Tipo de Petición")
    est_final = fields.Char(string="Estado Final")
    msg_conductor = fields.Char(string="Mensaje para el Conductor")
    distr_origen = fields.Char(string="Distrito Origen (Distrito 1)")
    direc_origen = fields.Char(string="Dirección Origen (Dirección 1)")
    distr_destino = fields.Char(string="Distrito Origen (Distrito 1)")
    direc_destino = fields.Char(string="Dirección Origen (Dirección 1)")
    num_vale = fields.Char(string="Numero de Vale")

    #Comentario de No aprobado
    commentary = fields.Text(string="Comentario")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
