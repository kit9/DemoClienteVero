from odoo import models, fields, api
import logging
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from openerp.http import request
from urllib.request import urlopen
import zipfile
from io import BytesIO

_logger = logging.getLogger(__name__)


class GeneralActions(models.Model):
    _name = 'sunat.general_actions'
    _description = "Sunat Tipo de Cambio"

    def sunat_type_currency(self):
        cambios = self.get_type_currency()
        cambios = cambios.split("|")
        compra = float(cambios[0])
        venta = float(cambios[1])

        # Monedas
        moneda_compra = self.env['res.currency'].search([('name', 'like', 'USD'), ('type', 'like', 'purchase')],
                                                        limit=1)
        moneda_venta = self.env['res.currency'].search([('name', 'like', 'USD'), ('type', 'like', 'sale')], limit=1)

        # Tipos de cambio
        cambio_compra = self.env['res.currency.rate'].search([('name', 'like', str(datetime.now().date())),
                                                              ('currency_id', 'like', moneda_compra.id)
                                                              ], limit=1)
        cambio_venta = self.env['res.currency.rate'].search([('name', 'like', str(datetime.now().date())),
                                                             ('currency_id', 'like', moneda_venta.id)
                                                             ], limit=1)

        if cambio_compra:
            _logger.info("Registro compra existe")
            cambio_compra.write({
                'rate_pe': compra or 0.0
            })
        else:
            _logger.info("Registro compra no existe")
            registro_nuevo = {
                'name': str(datetime.now().date()) or False,
                'rate_pe': compra or 0.0,
                'currency_id': moneda_compra and moneda_compra.id or False
            }
            _logger.info("Creando Registro compra -> " + str(registro_nuevo))
            cambio_compra = self.env['res.currency.rate'].create(registro_nuevo)

        if cambio_venta:
            _logger.info("Registro venta existe")
            cambio_venta.write({
                'rate_pe': venta or 0.0
            })
        else:
            _logger.info("Registro venta no existe")
            registro_nuevo = {
                'name': str(datetime.now().date()) or False,
                'rate_pe': venta or 0.0,
                'currency_id': moneda_venta and moneda_venta.id or False
            }
            _logger.info("Creando Registro venta -> " + str(registro_nuevo))
            cambio_venta = self.env['res.currency.rate'].create(registro_nuevo)
        cambio_compra.onchange_rate_pe()
        cambio_venta.onchange_rate_pe()

        return True

    def get_type_currency(self):
        url = 'http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias'
        # _logger.info("Inicio del metodo")
        # Crear un manejador, página, para manejar los contenidos del sitio web
        page = requests.get(url)

        soup = BeautifulSoup(page.text, 'lxml')
        table = soup.find("table", attrs={'class': 'class="form-table"'})

        encontrado = False
        compra = 0
        venta = 0

        dia_actual = int(time.strftime("%d"))
        # dia_actual = 2
        # _logger.info(dia_actual)

        tr_elements = table.find_all("tr")
        tr_num = len(tr_elements) - 1
        # tr_num = tr_num - 1
        for i in range(tr_num):
            i = i + 1
            td_elements = tr_elements[i].find_all("td")
            td_num = len(td_elements)
            if (td_num > 0):
                dia = int(td_elements[0].get_text().strip())
                if (dia_actual == dia):
                    encontrado = True
                    compra = float(td_elements[0 + 1].get_text().strip())
                    venta = float(td_elements[0 + 2].get_text().strip())
            if (td_num > 3):
                dia = int(td_elements[3].get_text().strip())
                if (dia_actual == dia):
                    encontrado = True
                    compra = float(td_elements[3 + 1].get_text().strip())
                    venta = float(td_elements[3 + 2].get_text().strip())
            if (td_num > 6):
                dia = int(td_elements[6].get_text().strip())
                if (dia_actual == dia):
                    encontrado = True
                    compra = float(td_elements[6 + 1].get_text().strip())
                    venta = float(td_elements[6 + 2].get_text().strip())
            if (td_num > 9):
                dia = int(td_elements[9].get_text().strip())
                if (dia_actual == dia):
                    encontrado = True
                    compra = float(td_elements[9 + 1].get_text().strip())
                    venta = float(td_elements[9 + 2].get_text().strip())

        if not encontrado:
            elemento = tr_elements[tr_num].find_all("td")
            numero = len(elemento) - 3
            compra = float(elemento[numero + 1].get_text().strip())
            venta = float(elemento[numero + 2].get_text().strip())
        #     _logger.info("No encontrado muestra por Defecto")
        #     _logger.info("compra -> " + str(compra) + " || venta -> " + str(venta))
        # else:
        #     _logger.info("Encontrado")
        #     _logger.info("compra -> " + str(compra) + " || venta -> " + str(venta))

        return str(compra) + "|" + str(venta)

    def sunat_buen_contribuyente(self):

        url = "http://www.sunat.gob.pe/descarga/BueCont/BueCont_TXT.zip"

        try:
            response = urlopen(url)
            zip = zipfile.ZipFile(BytesIO(response.read()))

            file = zip.read('BueCont_TXT.txt')

            datos = file.decode("windows-1252")

            # datos = datos.replace("\r", "\r\n")
            # lista = datos.split("\r\n");

            lista = datos.split("\r");
            _logger.info(len(lista))

            proveedores = request.env['res.partner'].sudo().search([('is_company', '=', 'True')])
            for proveedor in proveedores:
                proveedor.buen_contribuyente = False

            for line in lista:
                # _logger.info(len(lista))
                campos = line.split("|")
                proveedor = request.env['res.partner'].sudo().search(
                    [('is_company', '=', 'True'), ('vat', 'like', campos[0])], limit=1)
                if proveedor.catalog_06_id.code == "6":
                    proveedor.buen_contribuyente = True

        except requests.exceptions.ConnectionError as e:
            _logger.info("No se realizo la caneccion")
            return "No se realizo la caneccion"

        return "Completo"

    def sunat_agente_retencion(self):

        url = "http://www.sunat.gob.pe/descarga/AgentRet/AgenRet_TXT.zip"

        try:
            response = urlopen(url)
            zip = zipfile.ZipFile(BytesIO(response.read()))

            file = zip.read('AgenRet_TXT.txt')

            datos = file.decode("windows-1252")

            # datos = datos.replace("\r", "\r\n")
            # lista = datos.split("\r\n");

            lista = datos.split("\r");
            _logger.info(len(lista))

            proveedores = request.env['res.partner'].sudo().search([('is_company', '=', 'True')])
            for proveedor in proveedores:
                proveedor.age_retencion = False

            for line in lista:
                # _logger.info(len(lista))
                campos = line.split("|")
                proveedor = request.env['res.partner'].sudo().search(
                    [('is_company', '=', 'True'), ('vat', 'like', campos[0])], limit=1)
                if proveedor.catalog_06_id.code == "6":
                    proveedor.age_retencion = True

        except requests.exceptions.ConnectionError as e:
            _logger.info("No se realizo la caneccion")
            return "No se realizo la caneccion"

        return "Completo"

    def sunat_agente_percepcion(self):

        url = "http://www.sunat.gob.pe/descarga/AgentRet/AgenPercVI_TXT.zip"

        try:
            response = urlopen(url)
            zip = zipfile.ZipFile(BytesIO(response.read()))

            file = zip.read('AgenPercVI_TXT.txt')

            datos = file.decode("windows-1252")

            # datos = datos.replace("\r", "\r\n")
            # lista = datos.split("\r\n");

            lista = datos.split("\r");
            _logger.info(len(lista))

            proveedores = request.env['res.partner'].sudo().search([('is_company', '=', 'True')])
            for proveedor in proveedores:
                proveedor.age_percepcion = False

            for line in lista:
                # _logger.info(len(lista))
                campos = line.split("|")
                proveedor = request.env['res.partner'].sudo().search(
                    [('is_company', '=', 'True'), ('vat', 'like', campos[0])], limit=1)
                if proveedor.catalog_06_id.code == "6":
                    proveedor.age_percepcion = True

        except requests.exceptions.ConnectionError as e:
            _logger.info("No se realizo la caneccion")
            return "No se realizo la caneccion"

        return "Completo"
