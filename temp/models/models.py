# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    response = fields.Text(string="Response")

    # Tabla de Personas Juridicas
    # sunat_legal_person_id = fields.Many2one('sunat.legal_persons', 'Sunat Persona Juridica')

    # Datos Persona Juridica
    retention_agent = fields.Boolean(string="Agente de Retención", related="sunat_legal_person_id.retention_agent")
    # good_contributor = fields.Boolean(string="Buen Contribuyente", related="sunat_legal_person_id.good_contributor")
    # perception_agent = fields.Boolean(string="Agente de Percepción", related="sunat_legal_person_id.perception_agent")

    # Datos Persona Juridica
    # age_retencion = fields.Boolean(string="Agente de Retención")
    # buen_contribuyente = fields.Boolean(string="Buen Contribuyente")
    # age_percepcion = fields.Boolean(string="Agente de Percepción")
    # retention_agent = fields.Boolean(string="Agente de Retención", related="sunat_legal_person_id.retention_agent")
    # good_contributor = fields.Boolean(string="Buen Contribuyente", related="sunat_legal_person_id.good_contributor")
    # perception_agent = fields.Boolean(string="Agente de Percepción", related="sunat_legal_person_id.perception_agent")
