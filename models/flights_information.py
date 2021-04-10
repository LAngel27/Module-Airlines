# -*- coding: utf-8 -*-
from odoo import models,fields,api
from odoo.exceptions import UserError,Warning
import requests

# api_search_airlines = 'http://api.aviationstack.com/v1/airlines?&airline_name=American Airlines&access_key=4c24fbe3293e6eed9cdf2f2ca84a6cdb'

class InfoFlights(models.Model):
    _name = 'flights.info'
    _description = 'modelo sobre informacion de vuelos disponibles en tiempo real'


    airline_id = fields.Many2one(
        string='Buscar vuelo',
        comodel_name='registry',
        ondelete='restrict',
        required=True,

    )
    flight_date = fields.Datetime(string='Fecha de vuelo', readonly=True)
    flight_status = fields.Char(
        string='Estado del vuelo',
    )
    departure = fields.Char(string='salida')
    arrival = fields.Char(string='Llegada')
    flight_code = fields.Char(string='Codigo del vuelo',required=True)
    timezone = fields.Char(string='Zona horaria')
    iata_departure = fields.Char(string='IATA salida')
    iata_arrival = fields.Char(string='IATA llegada')
    flight_number = fields.Char(string='Nro. del vuelo')
    active = fields.Selection(selection=[('ar','archivado'), ('se', 'seguir')], default='ar')
    

    @api.multi
    @api.onchange('airline_id')
    def _onchange_info_flights(self):
        for record in self:
            api_result = requests.get(f'http://api.aviationstack.com/v1/flights?airline_name={record.airline_id.name}&access_key=4c24fbe3293e6eed9cdf2f2ca84a6cdb')
            if record.airline_id and api_result.status_code == 200:
                api_response = api_result.json()
                for data in api_response['data']:
                    record.flight_date = data['flight_date']
                    record.flight_status = data['flight_status']
                    record.departure = data['departure']['airport']
                    record.arrival = data['arrival']['airport']
                    record.flight_code = data['flight']['iata']
                    record.timezone = data['arrival']['timezone']
                    record.iata_departure = data['arrival']['iata']
                    record.iata_arrival = data['departure']['iata']
                    record.flight_number = data['flight']['number']
    
    
    @api.model
    def create(self, values):
        result = super(InfoFlights, self).create(values)
        if values['flight_status'] == 'landed':
            raise UserError('No se puede crear vuelos en estado landed')
        return result

    
    @api.multi
    def write(self,values):
        for record in self:
            if record.flight_status == 'scheduled':
                raise Warning('No se puede modificar un vuelo en estado programado')
        return super(InfoFlights, self).write(values)
    
