# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009-TODAY Odoo Peru(<http://www.odooperu.pe>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import logging
from odoo import models, fields, api
from odoo.exceptions import Warning

import requests


def get_data_doc_number(tipo_doc, numero_doc, format='json'):
    user, password = 'demorest', 'demo1234'
    if tipo_doc == 'dni':
        url = 'http://aplicaciones007.jne.gob.pe/srop_publico/Consulta/Afiliado/GetNombresCiudadano?DNI='
        url = '%s%s' % (url, str(numero_doc))
    else:
        url = 'http://py-devs.com/api'
        url = '%s/%s/%s' % (url, tipo_doc, str(numero_doc))
    res = {'error': True, 'message': None, 'data': {}}
    try:
        if tipo_doc == 'dni':
            response = requests.get(url)
        else:
            response = requests.get(url, auth=(user, password))
    except requests.exceptions.ConnectionError as e:
        res['message'] = 'Error en la conexion'
        return res

    if response.status_code == 200:
        res['error'] = False
        if tipo_doc == 'dni':
            res['data'] = response.text
        else:
            res['data'] = response.json()
    else:
        try:
            res['message'] = response.json()['detail']
        except Exception as e:
            res['error'] = True
    return res


class ResPartner(models.Model):
    _inherit = 'res.partner'

    registration_name = fields.Char('Name', size=128, index=True)
    catalog_06_id = fields.Many2one('einvoice.catalog.06', 'Tipo Doc.', index=True)
    state = fields.Selection([('habido', 'Habido'), ('nhabido', 'No Habido')], 'State')

    # ~ tipo_contribuyente = fields.Char('Tipo de contribuyente')
    # ~ fecha_inscripcion = fields.Date('Fecha de inscripción')
    # ~ estado_contribuyente = fields.Char('Estado del contribuyente')
    # ~ agente_retencion = fields.Boolean('Agente de Retención')
    # ~ agente_retencion_apartir_del = fields.Date('A partir del')
    # ~ agente_retencion_resolucion = fields.Char('Resolución')
    # ~ sistema_emision_comprobante = fields.Char('Sistema emisión')
    # ~ sistema_contabilidad = fields.Char('Sistema contabilidad')
    # ~ ultima_actualizacion_sunat = fields.Date('Última actualización')

    @api.onchange('catalog_06_id', 'vat')
    def vat_change(self):
        self.update_document()

    @api.one
    def update_document(self):

        if not self.vat:
            return False
        if self.catalog_06_id and self.catalog_06_id.code == '1':
            # Valida DNI
            if self.vat and len(self.vat) != 8:
                raise Warning('El Dni debe tener 8 caracteres')
            else:
                resp = get_data_doc_number(
                    'dni', self.vat, format='json')
                if not resp['error']:
                    resp = resp['data']
                    part = resp.split("|")
                    if len(part[0]) > 0:
                        self.name = '%s %s %s' % (
                            part[2],
                            part[0],
                            part[1]
                        )
                        self.registration_name = self.name
                        self.person_type = "01-Persona Natural"
                        self.ape_pat = part[0]
                        self.ape_mat = part[1]
                        self.nombres = part[2]

        elif self.catalog_06_id and self.catalog_06_id.code == '6':
            # Valida RUC
            if self.vat and len(self.vat) != 11:
                raise Warning('El Ruc debe tener 11 caracteres')
            else:
                d = get_data_doc_number(
                    'ruc', self.vat, format='json')
                if d['error']:
                    return True
                d = d['data']
                # ~ Busca el distrito
                ditrict_obj = self.env['res.country.state']
                prov_ids = ditrict_obj.search([('name', '=', d['provincia']),
                                               ('province_id', '=', False),
                                               ('state_id', '!=', False)])
                dist_id = ditrict_obj.search([('name', '=', d['distrito']),
                                              ('province_id', '!=', False),
                                              ('state_id', '!=', False),
                                              ('province_id', 'in', [x.id for x in prov_ids])], limit=1)
                if dist_id:
                    self.district_id = dist_id.id
                    self.province_id = dist_id.province_id.id
                    self.state_id = dist_id.state_id.id
                    self.country_id = dist_id.country_id.id

                # Si es HABIDO, caso contrario es NO HABIDO
                tstate = d['condicion_contribuyente']
                if tstate == 'HABIDO':
                    tstate = 'habido'
                else:
                    tstate = 'nhabido'
                self.state = tstate

                self.name = d['nombre_comercial'] != '-' and d['nombre_comercial'] or d['nombre']
                self.registration_name = d['nombre']
                domicilio_fiscal = ""
                if d['domicilio_fiscal']:
                    domicilio_fiscal = d['domicilio_fiscal']
                    if domicilio_fiscal:
                        domicilio_fiscal = domicilio_fiscal + ((" " + d['departamento']) if d[
                            'departamento'] else "")

                        domicilio_fiscal = domicilio_fiscal + ((" - " + d['provincia']) if d[
                            'provincia'] else "")

                        domicilio_fiscal = domicilio_fiscal + ((" - " + d['distrito']) if d[
                            'distrito'] else "")
                        domicilio_fiscal = domicilio_fiscal.replace("  ", " ")
                self.street = domicilio_fiscal
                self.vat_subjected = True
                self.is_company = True
        else:
            True
