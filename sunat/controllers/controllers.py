# -*- coding: utf-8 -*-
from odoo import http
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response
import xlsxwriter
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from io import BytesIO
import zipfile
from zipfile import ZipFile
from urllib.request import urlopen

_logger = logging.getLogger(__name__)


class Sunat(http.Controller):

    @http.route('/excel/<int:param>', auth='public')
    def generar_excel(self, param):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # Some data we want to write to the worksheet.
        expenses = (
            ['Rent', 1000],
            ['Gas', 100],
            ['Food', 300],
            ['Gym', 50],
        )

        _logger.info("Parametro -> " + str(param))

        # Start from the first cell. Rows and columns are zero indexed.
        row = 0
        col = 0

        # Iterate over the data and write it out row by row.
        for item, cost in (expenses):
            worksheet.write(row, col, item)
            worksheet.write(row, col + 1, cost)
            row += 1

        # Write a total using a formula.
        worksheet.write(row, 0, 'Total')
        worksheet.write(row, 1, '=SUM(B1:B4)')

        workbook.close()
        output.seek(0)
        headers = Headers()
        headers.set('Content-Disposition', 'attachment', filename="demo.xlsx")
        # return Response('Hello World!')
        return Response(output.read(), mimetype='application/vnd.openxmlformats-'
                                                'officedocument.spreadsheetml.sheet', headers=headers)

    @http.route('/jcondori', auth='public')
    def sunat_proveedores(self):

        url = "http://www.sunat.gob.pe/descarga/BueCont/BueCont_TXT.zip"

        try:
            resp = urlopen(url)
            zip = zipfile.ZipFile(BytesIO(resp.read()))
            with zipfile.ZipFile(zip) as z:
                with z.open(zip) as f:
                    for line in f:
                        _logger.info(line)
            _logger.info("----")
            _logger.info("zip encontrado")
            # file = zip.read('BueCont_TXT.txt')
            # datos = str(file).split("|")
            # _logger.info("Archivo Leido")
            # _logger.info(datos[0])
            # _logger.info(datos[1])
            # _logger.info(datos[2])
            # _logger.info(datos[3])
            # _logger.info(datos[4])
            # _logger.info(datos[5])
            # _logger.info(datos[6])
            # _logger.info(datos[7])
            # _logger.info(datos[8])
            # _logger.info(datos[9])
            # _logger.info(datos[10])

        except requests.exceptions.ConnectionError as e:
            _logger.info("No se realizo la caneccion")
            return "Hola"

        return "Hola"

    @http.route('/demo', auth='public')
    def obtener_cambio(self):
        url = 'http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias'

        # Crear un manejador, página, para manejar los contenidos del sitio web
        page = requests.get(url)

        soup = BeautifulSoup(page.text, 'lxml')
        table = soup.find("table", attrs={'class': 'class="form-table"'})

        encontrado = False
        compra = 0
        venta = 0

        dia_actual = int(datetime.now().date().strftime("%d"))
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

        resultado = ""

        if not encontrado:
            elemento = tr_elements[tr_num].find_all("td")
            numero = len(elemento) - 3
            compra = float(elemento[numero + 1].get_text().strip())
            venta = float(elemento[numero + 2].get_text().strip())
            resultado = "No encontrado muestra por Defecto"
            resultado = resultado + "\n" + "compra -> " + str(compra) + " || venta -> " + str(venta)
        else:
            resultado = "Encontrado"
            resultado = resultado + "\n" + "compra -> " + str(compra) + " || venta -> " + str(venta)

            resultado = resultado + "\n" + str(datetime.now().date())

        return resultado
