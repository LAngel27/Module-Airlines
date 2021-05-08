# -*- coding: utf-8 -*-
from odoo import fields,models,api
import base64
import xlwt
from io import BytesIO
from datetime import datetime

class ReportFlightToday(models.TransientModel):
    _name = 'report.today.flights'

    def print_report_xlsx(self):

        workbook = xlwt.Workbook(encoding='utf-8')
        sheet = workbook.add_sheet('Vuelos')
        today = datetime.now().date()
        file_name = 'Vuelos ' + str(today)
        sheet.write(0, 0, 'ID')
        sheet.write(0, 1, 'Aerolinea')
        sheet.write(0, 2,'fecha')
        sheet.write(0, 3, 'Codigo del vuelo')
        sheet.write(0, 4, 'Salida')
        sheet.write(0, 5, 'Llegada')
        flights = self.get_flights_today()
        for line,vals in enumerate(flights,1) :
            sheet.write(line, 0, vals['id'])
            sheet.write(line, 1, vals['airline_id'][1])
            sheet.write(line, 2, str(vals['flight_date']))
            sheet.write(line, 3, vals['flight_code'])
            sheet.write(line, 4, vals['departure'])
            sheet.write(line, 5, vals['arrival'])

        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        data_b64 = base64.encodestring(data)
        doc = self.env['ir.attachment'].create({'name': f'{(file_name)}.xls', 'datas': data_b64,'datas_fname': f'{(file_name)}.xls','type': 'url'})
        return {
            'type': "ir.actions.act_url",
            'url': "web/content/?model=ir.attachment&id=" + str(doc.id) + "&filename_field=datas_fname&field=datas&download=true&filename=" + str(doc.name),
            'target': "current",
            'no_destroy': False,
        }
    

    def get_flights_today(self):
        today = datetime.now().date()
        res = self.env['flights.info'].search([('flight_date', '=', today)])
        flights = res.read(['id','airline_id','flight_date','flight_code','departure','arrival'])
        return flights
