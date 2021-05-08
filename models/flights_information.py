# -*- coding: utf-8 -*-
from odoo import fields,models,api
from odoo.exceptions import UserError
import random
import requests

# api_search_airlines = 'http://api.aviationstack.com/v1/airlines?&airline_name=American Airlines&access_key=4c24fbe3293e6eed9cdf2f2ca84a6cdb'
class InfoFlights(models.Model):
    _name = 'flights.info'
    _description = 'modelo sobre informacion de vuelos disponibles y activos en tiempo real'


    name = fields.Char(string="Vuelos", default="New")
    airline_id = fields.Many2one('registry',string='Buscar vuelo', required=True)
    ticket_line_ids = fields.One2many('ticket.flight','flight_id',string='ticket')
    flight_date = fields.Date(string='Fecha de vuelo')
    flight_status = fields.Char(string='Estado del vuelo')
    state = fields.Selection(string='estado', selection=[('draft', 'Borrador'), ('compl', 'Completado')],
                             default='draft')
    departure = fields.Char(string='salida')
    arrival = fields.Char(string='Llegada')
    flight_code = fields.Char(string='Codigo del vuelo')
    timezone = fields.Char(string='Zona horaria')
    iata_departure = fields.Char(string='IATA salida')
    iata_arrival = fields.Char(string='IATA llegada')
    flight_number = fields.Char(string='Nro. del vuelo')
    status = fields.Selection(string='Status', selection=[('scheduled', 'Programado'), ('active', 'Activo')])
    

    def send_state_compl(self):
        self.state = 'compl'        
    
    def get_report_xlsx(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'report.today.flights',
            'view_id': self.env.ref('Airlines.report_flight_today_form_view').id,
            'target': 'new'
        }

    @api.multi
    def create_receivable(self):
        for record in self:
            account = self.env['account.invoice'].search([])
            account_account = self.env['account.account'].search([])
            res_partner = self.env['res.partner'].search([('name', '=', record.airline_id.name)])
            for line in record.ticket_line_ids:
                if record.flight_status == 'scheduled':
                    operation_create = account.create({
                            'transport_id': record.airline_id.id,
                            'partner_id': res_partner[0].id,
                            'date_invoice': record.flight_date,
                            'amount_total': line.cost_flight,
                    })

                    operation_create.write({ 'invoice_line_ids': [(0,0, {
                        'quantify': line.cost_flight,
                        'name': 'Boleto aereo',
                        'price_unit': line.cost_flight,
                        'invoice_id': operation_create.id,
                        'account_id': account_account[0].id
                    })]})
                else:
                    raise UserError('La compra no puede hacerse con un vuelo en status active')

    @api.multi
    @api.onchange('airline_id','status')
    def _onchange_info_flights(self):
        for record in self:
            query_airline = self.search([('airline_id.id', '=', record.airline_id.id)])
            flights = []
            randoms = random.randint(0, 99)
            api = f'http://api.aviationstack.com/v1/flights?airline_name={record.airline_id.name}&flight_status={record.status}&limit={randoms}&access_key=83d3c5d1cb2c1a010d3e2c375639bc0a'
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
                except requests.exceptions.ConnectionError:
                    raise UserError('En estos momentos no podemos solucionar su requerimiento compruebe su conexion a internet')

    
    @api.model
    def create(self, values):
        if values.get('name', 'New') == 'New':
                values['name'] = self.env['ir.sequence'].next_by_code('flights.info') or 'New'
        query = self.env['registry'].search([('id', '=', values['airline_id'])])
        if query.flights_total <= 0:
            query.update({
                'flights_total': 1,
            })
        elif query.flights_total > 0:
                query.update({
                    'flights_total': query.flights_total + 1,
            })
        return super(InfoFlights, self).create(values)

    @api.multi
    def unlink(self):
        for record in self:
            query = self.env['registry'].search([('id', '=', record.airline_id.id)])
            query.update({
                'flights_total': query.flights_total - 1 if query.flights_total > 0 else 0,
            })
        return super(InfoFlights, self).unlink()


class TicketFlights(models.Model):
    _name = 'ticket.flight'
    _rec_name = 'flight_id'

    flight_id = fields.Many2one('flights.info', string='Vuelo')
    date_flight = fields.Date(string='fecha')
    airline = fields.Char(string='Aerolinea')
    departures = fields.Char(string='Salida')
    arrivals = fields.Char(string='Llegada')
    cost_flight = fields.Float(string='Costo',compute='_compute_cost_flight')
    receivable = fields.Boolean('Por cobrar',readonly=True, default=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Metodo de pago')
    code = fields.Char(string='Codigo del vuelo')

    @api.model
    def create(self, values):
        query = self.search([('airline', '=', values['airline'])])
        if query:
            raise UserError('Ya hay ticket vinculado con este registro')
        else:
            return super(TicketFlights, self).create(values)

    @api.depends()
    def _compute_cost_flight(self):
        for record in self:
            record.cost_flight = 20 * 2000

    @api.multi
    @api.onchange('flight_id')
    def _onchange_flight(self):
        for record in self:
            for line in record.flight_id:
                record.airline = line.airline_id.display_name
                record.departures = line.departure
                record.arrivals = line.arrival
                record.date_flight = line.flight_date
                record.code = line.flight_code




    
