# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging
import pytz
from pytz import timezone, utc

_logger = logging.getLogger(__name__)


###########################################################################################
# -- OPTIMIZA
# -- DESCRIPCION: FUNCION PARA OBTENER EN NUMERO FLOAT CONVERTIDO EN HORAS
# -- AUTOR: JOSE LUIS CONDORI JARA
# -- CAMBIOS: FECHA (DD/MM/YYYY)  PERSONA               CAMBIOS EFECTUADOS
# --          23/05/2019          JOSE CONDORI          CREACION DE FUNCION.
# -----------------------------------------------------------------------------------------
def float_to_time(num_hour):
    v_hour = int(num_hour)
    v_minute = int((num_hour - v_hour) * 60)
    return timedelta(hours=v_hour, minutes=v_minute)


###########################################################################################
# -- OPTIMIZA
# -- DESCRIPCION: FUNCION PARA OBTENER EN NUMERO FLOAT CONVERTIDO EN HORAS
# -- AUTOR: JOSE LUIS CONDORI JARA
# -- CAMBIOS: FECHA (DD/MM/YYYY)  PERSONA               CAMBIOS EFECTUADOS
# --          29/05/2019          JOSE CONDORI          CREACION DE FUNCION.
# -----------------------------------------------------------------------------------------
def get_schedure_time(p_datetime, p_type):
    v_datetime = False
    if p_type == "ini":
        v_datetime = p_datetime.replace(hour=9, minute=0, second=0)
    elif p_type == "fin":
        v_datetime = p_datetime.replace(hour=19, minute=0, second=0)
    elif p_type == "resini":
        v_datetime = p_datetime.replace(hour=13, minute=0, second=0)
    elif p_type == "resfin":
        v_datetime = p_datetime.replace(hour=14, minute=0, second=0)
    elif p_type == "media":
        v_datetime = p_datetime.replace(hour=0, minute=0, second=0)
    if v_datetime:
        v_datetime = v_datetime + timedelta(hours=5)
    return v_datetime


###########################################################################################
# -- OPTIMIZA
# -- DESCRIPCION: FUNCION PARA OBTENER EN NUMERO FLOAT CONVERTIDO EN HORAS
# -- AUTOR: JOSE LUIS CONDORI JARA
# -- CAMBIOS: FECHA (DD/MM/YYYY)  PERSONA               CAMBIOS EFECTUADOS
# --          29/05/2019          JOSE CONDORI          CREACION DE FUNCION.
# -----------------------------------------------------------------------------------------
def validate_start_datetime(start_datetime):
    # Inicio -> Validaciones de Incio de la actividad
    if start_datetime >= get_schedure_time(start_datetime, "fin"):
        start_datetime = (get_schedure_time(start_datetime, "ini") + timedelta(days=1))
        _logger.info("Start -> Despues horario de Trabajo")
    if start_datetime < get_schedure_time(start_datetime, "ini"):
        start_datetime = get_schedure_time(start_datetime, "ini")
        _logger.info("Start -> Antes horario de Trabajo")
    # Fin -> Validaciones de Incio de la actividad
    return start_datetime


###########################################################################################
# -- OPTIMIZA
# -- DESCRIPCION: FUNCION PARA OBTENER EN NUMERO FLOAT CONVERTIDO EN HORAS
# -- AUTOR: JOSE LUIS CONDORI JARA
# -- CAMBIOS: FECHA (DD/MM/YYYY)  PERSONA               CAMBIOS EFECTUADOS
# --          29/05/2019          JOSE CONDORI          CREACION DE FUNCION.
# -----------------------------------------------------------------------------------------
def calculation_end_activity(start_datetime, duration):
    end_datetime = False
    dias = abs(int(duration / 9))
    horas = duration - (dias * 9)
    # _logger.info("Dias -> " + str(dias))
    # _logger.info("Horas -> " + str(horas))

    # -- Se calcula la hora de finalizacion de la Actividad
    if start_datetime:
        end_datetime = start_datetime + float_to_time(horas)

        # Inicio -> Validacion del receso en el incio de la actividad
        if dias <= 0:
            if end_datetime.day == start_datetime.day:
                # _logger.info("Actividad tratado en el mismo Dia")
                if start_datetime < get_schedure_time(start_datetime, "resini") and \
                        end_datetime >= get_schedure_time(end_datetime, "resfin"):
                    end_datetime = end_datetime + timedelta(hours=1)
                    # _logger.info("Agregando 1 hora del receso del mismo dia")
        elif dias > 0 and start_datetime < get_schedure_time(start_datetime, "resini"):
            end_datetime = end_datetime + timedelta(hours=1)
            # _logger.info("Agregando 1 hora del receso inicio de dias")
        # Fin -> Validacion del receso en el incio de la actividad

        # Inicio -> Suma de Dias
        if dias > 0:
            end_datetime = end_datetime + timedelta(days=dias)
            # _logger.info("Dias Agregados")
        # Fin -> Suma de Dias

        # Inicio -> Validacion del receso en el fin de la actividad
        if dias > 0 and end_datetime > get_schedure_time(end_datetime, "resini"):
            end_datetime = end_datetime + timedelta(hours=1)
            # _logger.info("Agregando 1 hora del receso fin de dias")
        # Fin -> Validacion del receso en el fin de la actividad

        # Inicio -> Validaciones de fin de la actividad
        # _logger.info("If " + str(end_datetime) + " > " + str(get_schedure_time(end_datetime, "fin")))
        # _logger.info(
        #     "or " + str(end_datetime) + " < " + str(get_schedure_time(end_datetime, "ini") + timedelta(days=1)))
        if (end_datetime > get_schedure_time(end_datetime, "fin") or \
            end_datetime == get_schedure_time(end_datetime, "media")) and \
                end_datetime < (get_schedure_time(end_datetime, "ini") + timedelta(days=1)):
            end_datetime = end_datetime + timedelta(hours=14)
            # _logger.info("Fuera del horario de Trabajo")
        # Fin -> Validaciones de fin de la actividad

        # _logger.info(start_datetime)
        # _logger.info(end_datetime)
        # _logger.info(start_datetime.strftime("%d/%m/%Y %I:%M:%S %p"))
        # _logger.info(end_datetime.strftime("%d/%m/%Y %I:%M:%S %p"))

    return end_datetime


###########################################################################################
# -- OPTIMIZA
# -- DESCRIPCION: CLASE HEREDADA DEL STANDAR PARA MODIFICARLO
# -- AUTOR: JOSE LUIS CONDORI JARA
# -- CAMBIOS: FECHA (DD/MM/YYYY)  PERSONA               CAMBIOS EFECTUADOS
# --          23/05/2019          JOSE CONDORI          CREACION DE LA CLASE.
# -----------------------------------------------------------------------------------------
class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    analysis_duration = fields.Float(string="Tiempo de Analisis")
    attention_duration = fields.Float(string="Tiempo de Atención")

    attention_datetime = fields.Datetime(string="Fecha Fin", compute="_get_attention_datetime", store=True, copy=False)

    queue_management_ids = fields.One2many("helpdesk.queue_management", "helpdesk_ticket_id", string='Tiempos',
                                           copy=False)

    @api.constrains('analysis_duration', 'attention_duration')
    def _check_durations(self):
        for record in self:
            if record.analysis_duration == 0.0 or record.attention_duration == 0.0:
                raise ValidationError("Necesita ingresar la duración del análisis y atención")

    @api.multi
    @api.depends('queue_management_ids')
    def _get_attention_datetime(self):
        for rec in self:
            list = sorted(rec.queue_management_ids, key=lambda x: x.end_datetime)
            if len(list) > 0:
                object = list[len(list) - 1]
                rec.attention_datetime = object.end_datetime

    @api.model
    def create(self, vals):
        res = super(HelpdeskTicket, self).create(vals)

        # Declaraciones
        model = self.env['helpdesk.queue_management']
        calendar = res.team_id.resource_calendar_id
        actual = False
        reorder = []
        temporaltime = False

        # datetime.now()
        now_datetime = fields.Datetime.now() - float_to_time(res.analysis_duration)

        realtime = fields.Datetime.now()

        models = model.search([('helpdesk_ticket_id.stage_id.is_close', '=', False),
                               ('user_id', '=', res.user_id.id)])

        next_attention = False
        for rec in models:
            if actual:
                reorder.append(rec)
            if rec.start_datetime <= now_datetime and rec.end_datetime >= now_datetime and not actual:
                actual = rec

        # models = models.filtered(lambda r: r.start_datetime <= now_datetime and r.end_datetime >= now_datetime)

        # -------------------------------------------------------------------------------
        #           Tratamos el tiempo actual
        # -------------------------------------------------------------------------------
        tiempo_restante = 0
        if actual:
            # actual = models[0]
            tiempo_real = calendar.get_work_hours_count(actual.start_datetime, now_datetime)
            if tiempo_real < 0.02:
                tiempo_real = 0.02
            tiempo_restante = calendar.get_work_hours_count(now_datetime, actual.end_datetime)
            actual.write({
                'duration': tiempo_real
            })
            now_datetime = actual.end_datetime + timedelta(minutes=1)

        # -------------------------------------------------------------------------------
        #           Tiempo de Analisis
        # -------------------------------------------------------------------------------
        queue_ana = False
        queue_ana_vals = {
            'name': str(res.name) + " - Analisis",
            'helpdesk_ticket_id': res and res.id or False,
            'start_datetime': now_datetime,
            'duration': res.analysis_duration,
            'is_analysis': True,
        }
        queue_ana = model.create(queue_ana_vals)
        temporaltime = queue_ana.end_datetime

        # -------------------------------------------------------------------------------
        #           Tratamos el tiempo actual
        # -------------------------------------------------------------------------------
        if actual:
            realtime = queue_ana.end_datetime + timedelta(minutes=1)
            tiempo_rest = {
                'name': actual.name,
                'helpdesk_ticket_id': actual.helpdesk_ticket_id and actual.helpdesk_ticket_id.id or False,
                'start_datetime': realtime,
                'duration': tiempo_restante,
                'is_analysis': actual.is_analysis,
            }
            temp = model.create(tiempo_rest)
            temporaltime = temp.end_datetime

        # -------------------------------------------------------------------------------
        #           Ordenamos los tickets
        # -------------------------------------------------------------------------------

        for rec in reorder:
            if temporaltime:
                rec.start_datetime = temporaltime
                temporaltime = rec.end_datetime

        # -------------------------------------------------------------------------------
        #           Tiempo de Atencion
        # -------------------------------------------------------------------------------
        last_datetime = self.get_last_date_by_user(res.user_id.id)

        if queue_ana.end_datetime > last_datetime:
            last_datetime = queue_ana.end_datetime

        if queue_ana:
            queue_ate_vals = {
                'name': str(res.name) + " - Atención",
                'helpdesk_ticket_id': res and res.id or False,
                # Sumamos es tiempo del anasis a la fecha de inicio de la solución
                'start_datetime': last_datetime + timedelta(minutes=1),
                # now_datetime + float_to_time(res.analysis_duration) + timedelta(minutes=1),
                'duration': res.attention_duration,
                'is_analysis': False,
            }
            queue_ate = model.create(queue_ate_vals)
            # res.queue_management_ate_id = queue_ate and queue_ate.id or False

        return res

    @api.model
    def get_last_date(self):
        last_queue = self.env['helpdesk.queue_management'].search([], order="start_datetime desc", limit=1)
        now_datetime = False
        if last_queue.end_datetime:
            if last_queue.end_datetime > datetime.now():
                now_datetime = last_queue.end_datetime
        if not now_datetime:
            now_datetime = datetime.now()
        return now_datetime

    @api.model
    def get_last_date_by_user(self, id_user):
        last_queue = self.env['helpdesk.queue_management'].search([('user_id', '=', id_user),
                                                                   ('helpdesk_ticket_id', '!=', self.id)],
                                                                  order="start_datetime desc", limit=1)
        now_datetime = False
        if last_queue.end_datetime:
            if last_queue.end_datetime > datetime.now():
                now_datetime = last_queue.end_datetime
        if not now_datetime:
            now_datetime = datetime.now()
        return now_datetime


###########################################################################################
# -- OPTIMIZA
# -- DESCRIPCION: NUEVA CLASE PARA CONTROL DE HORAS DE LOS TICKETS
# -- AUTOR: JOSE LUIS CONDORI JARA
# -- CAMBIOS: FECHA (DD/MM/YYYY)  PERSONA               CAMBIOS EFECTUADOS
# --          23/05/2019          JOSE CONDORI          CREACION DE LA CLASE.
# -----------------------------------------------------------------------------------------
class QueueManagement(models.Model):
    _name = 'helpdesk.queue_management'
    _description = "Fechas y Horas de los Tickets"

    name = fields.Char(string="Descripción")
    helpdesk_ticket_id = fields.Many2one(comodel_name="helpdesk.ticket", string="Ticket", ondelete="cascade",
                                         copy=False)
    start_datetime = fields.Datetime(string="Fecha Inicio", default=fields.Datetime.now)
    duration = fields.Float(string="Duración")
    is_analysis = fields.Boolean(string="Es un análisis", copy=False)
    end_datetime = fields.Datetime(string="Fecha Fin", compute="_get_end_datetime", store=True, copy=False)

    user_id = fields.Many2one(comodel_name="res.users", string="Usuario", related="helpdesk_ticket_id.user_id")

    @api.multi
    @api.depends('start_datetime', 'duration', 'helpdesk_ticket_id')
    def _get_end_datetime(self):
        for rec in self:
            calendar = rec.helpdesk_ticket_id.team_id.resource_calendar_id
            _logger.info(
                "Inicio -> " + rec.start_datetime.strftime("%d/%m/%Y %I:%M:%S %p") if rec.start_datetime else '')
            v_hour = int(rec.duration)
            v_minute = int((rec.duration - v_hour) * 60)
            _logger.info("Horas " + str(v_hour) + " y minutos " + str(v_minute))
            end = rec.start_datetime
            if calendar and v_hour > 0 and end:
                end = calendar.plan_hours(v_hour, rec.start_datetime, compute_leaves=True)
                if v_minute > 0:
                    end = end + timedelta(minutes=v_minute)
            elif calendar and v_minute > 0 and end:
                end = end + timedelta(minutes=v_minute)
            _logger.info("Fin    -> " + end.strftime("%d/%m/%Y %I:%M:%S %p") if end else '')
            rec.end_datetime = end

    # @api.model
    # def create(self, vals):
    #     queue_management = super(QueueManagement, self).create(vals)
    #     return queue_management
    #
    # @api.multi
    # def write(self, vals):
    #     queue_management = super(QueueManagement, self).write(vals)
    #     return queue_management
