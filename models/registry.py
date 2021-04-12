# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo.exceptions import UserError
import requests

# api_search_airlines = 'http://api.aviationstack.com/v1/airlines?&airline_name=American Airlines&access_key=4c24fbe3293e6eed9cdf2f2ca84a6cdb'

class AirRegistry(models.Model):
    _name = 'registry'
    _description = 'modelo de registro aereo'


    name = fields.Char(required=True,string='Nombre')
    origin = fields.Char(required=True,string="Sede")
    director = fields.Char(required=True, string='Director')
    sub_director = fields.Char(string='Subdirector')
    image = fields.Binary(required=True,help='Asegurese que sea el logo de la empresa')    
    state = fields.Selection(
        string='status',
        selection=[('draft', 'Borrador'), ('veri', 'Verifique'), ('confir','Confirmado')],
        default='draft',
    )
    iata_code = fields.Char(string='IATA', help='El código IATA de la aerolínea')
    website = fields.Char(string='Website',help='coloque direccion url')
    email = fields.Char(string='Email')
    phone_central = fields.Char(string='Central telefonica', required=True)
    callsign = fields.Char(string="OACI", required=True, help='El indicativo OACI de la aerolínea')
    category = fields.Many2one(
        string='Categoria',
        comodel_name='res.partner.category',
        ondelete='restrict',
    )
    document = fields.Binary(help='En formato pdf')
    icao_code = fields.Char(string="ICAO",help='El código ICAO de la aerolínea.')
    fleet_size = fields.Char(string="Flota")
    description_privacy_policy = fields.Text(string='Politicas de privacidad')
    names = fields.Integer(string='Vuelos disponibles')
    
    def continues(self):
        self.state = 'veri'
    
    def continues_veri(self):
        self.state = 'confir'

    def get_flight(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vuelos',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'flights.info',
            'domain': [('airline_id', '=', self.id)],
            'context': "{'create': False}"
        }
    
    @api.model
    def create(self, values):
        domain = [('name', '=', values['name']), ('iata_code', '=', values['iata_code'])]
        query = self.search_count(domain)
        if query > 0:
            raise UserError(f'Ya existe un registro con el nombre {values["name"]} y el IATA {values["iata_code"]}')
        else:
            return super(AirRegistry,self).create(values)
    
    
    
    @api.multi
    def unlink(self):
        for record in self:
            if record.state == 'confir':
                raise UserError('No se puede modificar un registro en estado confirmado')
        return super(AirRegistry, self).unlink()
    
    @api.multi
    def sending_data_to_the_partner_and_update_models(self):
        res = self.env['res.partner']
        for record in self:
            res_count = self.env['res.partner'].search_count([('name','=',record.name)])
            res_id_partner = self.env['res.partner'].search([('name','=',record.name)])
            if record.state == 'confir' and res_count <= 0:
                values = {
                    'name': record.name,
                    'image': record.image,
                    'email': record.email,
                    'website': record.website,
                    'phone': record.phone_central,
                    'street': record.origin,
                }
                res.create(values)
                self.sending_data_airlines_affiliates()
            elif res_count > 0:
                res = res_id_partner
                values = {
                    'image': record.image,
                    'email': record.email,
                    'website': record.website,
                    'phone': record.phone_central,
                    'street': record.origin,
                    'category_id': record.category
                }
                res.write(values)
                self.write_data_airlines_affiliates()

    @api.multi
    def sending_data_airlines_affiliates(self):
        res_affiliates = self.env['airlines.affiliates']
        for record in self:
            values = {
                    'company_name': record.name,
                    'phone': record.phone_central,
                    'direct': record.director,
                    'image': record.image,
                    'iata': record.iata_code,
                }
            send = res_affiliates.create(values)
        return send

    @api.multi
    def write_data_airlines_affiliates(self):
        for record in self:
            res_affiliates = self.env['airlines.affiliates'].search([('company_name', '=', record.name)])
            values = {
                'company_name': record.name,
                'phone': record.phone_central,
                'direct': record.director,
                'image': record.image,
                'iata': record.iata_code,
            }
            write = res_affiliates.write(values)
        return write

    @api.multi
    @api.onchange('name')
    def onchange_search_airline(self):
        for record in self:
            try:
                api_get = requests.get(f'http://api.aviationstack.com/v1/airlines?airline_name={record.name}&access_key=c841a935043ceac1a52dafe03c94ea5b')
                if api_get.status_code == 200 and record.name:
                    api_response = api_get.json()
                    for data in api_response['data']:
                        record.names = self.env['flights.info'].search_count([('airline_id', '=', record.name)])
                        record.origin = data['country_name']
                        record.icao_code = data['icao_code']
                        record.iata_code = data['iata_code']
                        record.callsign = data['callsign']
                        record.fleet_size = data['fleet_size']
                    if not record.callsign and not record.iata_code:
                        raise UserError(f'No encontramos una aerolinea con el nombre {record.name}')
                    elif record.names <= 0 and record.state == 'veri':
                        res = self.env['flights.info']
                        vals = {
                            'airline_id': record.id,
                        }
                        res.create(vals)
            except requests.exceptions.ConnectionError:
                raise UserError('En estos momentos no podemos solucionar su requerimiento compruebe su conexion a internet')


    # def print_report(self):
    #     return self.env.ref('Airlines.action_report_airlines_registry').report_action(self)
        # view
        # return {
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'airlines.affiliates',
        # }

        # wizard_id = self.env.ref('Airlines.contract_report_view').id

        # return {
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'report.taks',
        #     'view_id': wizard_id,
        #     'target': 'new',
        # }



