# -*- coding: utf-8 -*-
from odoo import fields,models,api
from odoo.exceptions import UserError
import random
import requests

# api_search_airlines = 'http://api.aviationstack.com/v1/airlines?&airline_name=American Airlines&access_key=4c24fbe3293e6eed9cdf2f2ca84a6cdb'
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
    state = fields.Selection(string='estado', selection=[('draft', 'Borrador'), ('compl', 'Completado')],default='draft')
    departure = fields.Char(string='salida')
    arrival = fields.Char(string='Llegada')
    flight_code = fields.Char(string='Codigo del vuelo')
    timezone = fields.Char(string='Zona horaria')
    iata_departure = fields.Char(string='IATA salida')
    iata_arrival = fields.Char(string='IATA llegada')
    flight_number = fields.Char(string='Nro. del vuelo')
    # numbers = fields.Float(compute='_compute_cost_product', string='balance')
    flights_total = fields.Integer(string='Total de vuelos',readonly=True)
    status = fields.Selection(string='Status', selection=[('sched', 'Programado'), ('acti', 'Activo')])
    
    """ @api.depends('amount_total','amount')
    def _compute_cost_product(self):
        for record in self:
            total = record.amount
            record.numbers = 10
            record.amount_total = total * record.numbers """
    

    def send_state_compl(self):
        self.state = 'compl'
    
    def get_report_xlsx(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'report.today.flights',
            'view_id': self.env.ref('Airlines.report_generator_form_view').id,
            'target': 'new'
        }

    # def fn(self):
    #   pass


    @api.multi
    @api.onchange('airline_id','status','total')
    def _onchange_info_flights(self):
        for record in self:
            randoms = random.randint(0, 99)
            api = f'http://api.aviationstack.com/v1/flights?airline_name={record.airline_id.name}&status={record.status}&limit={randoms}&access_key=83d3c5d1cb2c1a010d3e2c375639bc0a'
            if record.airline_id and record.status:
                try:
                    api_request = requests.get(api)
                    if record.airline_id and api_request.status_code == 200:
                        api_response = api_request.json()
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
                            record.flights_total = len(api_response['data'])
                except requests.exceptions.ConnectionError:
                    raise UserError('En estos momentos no podemos solucionar su requerimiento compruebe su conexion a internet')

    @api.multi
    def write(self, values):
        if values['flight_status'] == 'scheduled':
            raise UserError('No se puede modificar un vuelo en estado programado')
        return super(InfoFlights, self).write(values)
    
    @api.model
    def create(self, values):
        query = self.env['registry'].search([('id', '=', values['airline_id'])])
        if query.names <= 0:
            query.update({
                'names': 1,
            })
        elif query.names > 0:
                query.update({
                    'names': query.names + 1,
            })
        return super(InfoFlights, self).create(values)

    @api.multi
    def unlink(self):
        query = self.env['registry'].search([('id', '=', self.airline_id.id)])
        if query:
            query.update({
                'names': query.names - 1,
            })
        return super(InfoFlights, self).unlink()
