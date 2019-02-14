# -*- coding: utf-8 -*-
from odoo import http
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response
from io import BytesIO
import xlsxwriter
import logging
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup


_logger = logging.getLogger(__name__)


class Sunat(http.Controller):

    # @http.route('/demo', auth='public')
    # def obtener_cambio(self):
    #     url = 'http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias'
    #
    #     # Crear un manejador, página, para manejar los contenidos del sitio web
    #     page = requests.get(url)
    #
    #     soup = BeautifulSoup(page.text, 'lxml')
    #     table = soup.find("table", attrs={'class': 'class="form-table"'})
    #
    #     encontrado = False
    #     compra = 0
    #     venta = 0
    #
    #     dia_actual = int(time.strftime("%d"))
    #     # dia_actual = 2
    #     _logger.info(dia_actual)
    #
    #     tr_elements = table.find_all("tr")
    #     tr_num = len(tr_elements) - 1
    #     # tr_num = tr_num - 1
    #     for i in range(tr_num):
    #         i = i + 1
    #         td_elements = tr_elements[i].find_all("td")
    #         td_num = len(td_elements)
    #         if (td_num > 0):
    #             dia = int(td_elements[0].get_text().strip())
    #             if (dia_actual == dia):
    #                 encontrado = True
    #                 compra = float(td_elements[0 + 1].get_text().strip())
    #                 venta = float(td_elements[0 + 2].get_text().strip())
    #         if (td_num > 3):
    #             dia = int(td_elements[3].get_text().strip())
    #             if (dia_actual == dia):
    #                 encontrado = True
    #                 compra = float(td_elements[3 + 1].get_text().strip())
    #                 venta = float(td_elements[3 + 2].get_text().strip())
    #         if (td_num > 6):
    #             dia = int(td_elements[6].get_text().strip())
    #             if (dia_actual == dia):
    #                 encontrado = True
    #                 compra = float(td_elements[6 + 1].get_text().strip())
    #                 venta = float(td_elements[6 + 2].get_text().strip())
    #         if (td_num > 9):
    #             dia = int(td_elements[9].get_text().strip())
    #             if (dia_actual == dia):
    #                 encontrado = True
    #                 compra = float(td_elements[9 + 1].get_text().strip())
    #                 venta = float(td_elements[9 + 2].get_text().strip())
    #
    #     if not encontrado:
    #         elemento = tr_elements[tr_num].find_all("td")
    #         numero = len(elemento) - 3
    #         compra = float(elemento[numero + 1].get_text().strip())
    #         venta = float(elemento[numero + 2].get_text().strip())
    #         _logger.info("No encontrado muestra por Defecto")
    #         _logger.info("compra -> " + str(compra) + " || venta -> " + str(venta))
    #     else:
    #         _logger.info("Encontrado")
    #         _logger.info("compra -> " + str(compra) + " || venta -> " + str(venta))
    #
    #     _logger.info(str(datetime.now().date()))
    #
    #     # for tr in tr_elements:
    #     #     _logger.info(len(tr.find_all("td")))
    #     #     for td in tr.find_all("td"):
    #     #         _logger.info(td.get_text().strip() + " -> " + str(len(td.get_text().strip())))
    #
    #     # for t in tr_elements:
    #     #     _logger.info(str(t.text_content()))
    #     return table.get_text()
