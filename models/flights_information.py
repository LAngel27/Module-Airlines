# -*- coding: utf-8 -*-
from odoo import models,fields,api
from odoo.exceptions import UserError,Warning
import requests

# api_search_airlines = 'http://api.aviationstack.com/v1/airlines?&airline_name=American Airlines&access_key=4c24fbe3293e6eed9cdf2f2ca84a6cdb'
# api = 'http://api.aviationstack.com/v1/?access_key=c841a935043ceac1a52dafe03c94ea5b' hotmail
class InfoFlights(models.Model):
    _name = 'flights.info'
    _description = 'modelo sobre informacion de vuelos disponibles en tiempo real'


    airline_id = fields.Many2one(
        string='Buscar vuelo',
        comodel_name='registry',
        required=True,

    )
    flight_date = fields.Datetime(string='Fecha de vuelo')
    flight_status = fields.Char(
        string='Estado del vuelo',
    )
    departure = fields.Char(string='salida')
    arrival = fields.Char(string='Llegada')
    flight_code = fields.Char(string='Codigo del vuelo')
    timezone = fields.Char(string='Zona horaria')
    iata_departure = fields.Char(string='IATA salida')
    iata_arrival = fields.Char(string='IATA llegada')
    flight_number = fields.Char(string='Nro. del vuelo')
    

    @api.multi
    @api.onchange('airline_id')
    def _onchange_info_flights(self):
        for record in self:
            try:
                api_result = requests.get(f'http://api.aviationstack.com/v1/flights?airline_name={record.airline_id.name}&access_key=c841a935043ceac1a52dafe03c94ea5b')
                if record.airline_id and api_result.status_code == 200:
                    api_response = api_result.json()
                    for data in api_response['data']:
                        vals = {
                            'record.flight_date': data['flight_date'],
                            'record.flight_status': data['flight_status'],
                            'record.departure': data['departure']['airport'],
                            'record.arrival': data['arrival']['airport'],
                            'record.flight_code': data['flight']['iata'],
                            'record.timezone': data['arrival']['timezone'],
                            'record.iata_departure': data['arrival']['iata'],
                            'record.iata_arrival': data['departure']['iata'],
                            'record.flight_number': data['flight']['number']
                        }
                        self.create(vals)
            except requests.exceptions.ConnectionError:
                raise UserError('En estos momentos no podemos solucionar su requerimiento compruebe su conexion a internet')
                    #     wizard_id = self.env.ref('Airlines.contract_report_view').id

                    #     return {
                    #         'type': 'ir.actions.act_window',
                    #         'view_type': 'form',
                    #         'view_mode': 'form',
                    #         'res_model': 'report.taks',
                    #         'view_id': wizard_id,
                    #         'target': 'new',
                    #     }

    
    
    '''    @api.model
    def create(self, values):
        result = super(InfoFlights, self).create(values)
        if values['flight_status'] == 'landed':
            raise UserError('No se puede crear vuelos en estado landed')
        return result '''

    
    @api.multi
    def write(self,values):
        for record in self:
            if record.flight_status == 'scheduled':
                raise Warning('No se puede modificar un vuelo en estado programado')
        return super(InfoFlights, self).write(values)
    
# class InfoAirlineFlight(models.Model):
#     _inherit = 'registry'

#     names = fields.Char(string='Vuelos disponibles')



#     @api.multi
#     @api.onchange('')
#     def _onchange_get_flights_available(self):
#         pass
