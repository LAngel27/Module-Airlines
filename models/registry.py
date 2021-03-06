# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo.exceptions import UserError
import requests
# api_search_airlines = 'http://api.aviationstack.com/v1/airlines?&airline_name=American Airlines&access_key=83d3c5d1cb2c1a010d3e2c375639bc0a'

class AirRegistry(models.Model):
    _name = 'registry'
    _description = 'modelo de registro aereo'


    name = fields.Char(required=True,string='Nombre')
    user_id = fields.Many2one('res.users')
    origin = fields.Char(required=True,string="Sede")
    director = fields.Char(required=True, string='Director')
    sub_director = fields.Char(string='Subdirector')
    image = fields.Binary(help='Asegurese que sea el logo de la empresa')    
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
    category = fields.Many2one('res.partner.category',string='Categoria')
    document = fields.Binary(help='En formato pdf')
    icao_code = fields.Char(string="ICAO",help='El código ICAO de la aerolínea.')
    fleet_size = fields.Char(string="Flota")
    description_privacy_policy = fields.Text(string='Politicas de privacidad')
    flights_total = fields.Integer(string='Vuelos disponibles')

    
    def continues(self):
        self.state = 'veri'

    
    def continues_veri(self):
        self.state = 'confir'

    def get_report(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Comprobante',
            'res_model': 'report.registry',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('Airlines.registry_report_view').id,
            'target': 'new'
        }

    def get_view_registry_electronic(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Registro electronico',
            'res_model': 'registry.electronic',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('Airlines.registry_electronic_view_form').id,
            'target': 'new'
        }


    def get_flight(self):
        ctx = {'create': False}
        # 'edit': True,
        # 'search_default_name': 'Qatar Airways' # debe estar definido en la vista search
        # 'create': False

        return {
            'type': 'ir.actions.act_window',
            'name': 'Vuelos Disponibles',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'flights.info',
            'domain': [('airline_id', '=', self.id)],
            'context': ctx
        }

    def get_flights(self):
        query = self.env['flights.info'].search_read([('airline_id', '=', self.id)])
        if query:
            return query

    
    @api.model
    def create(self, values):
        domain = [('name', '=', values['name']), ('iata_code', '=', values['iata_code'])]
        query = self.search_count(domain)
        if query > 0:
            raise UserError(f'Ya existe un registro con el nombre {values["name"]} y el IATA {values["iata_code"]} borrador')
        else:
            return super(AirRegistry,self).create(values)
    
    @api.multi
    def action_send_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']

        try:
            template_id = ir_model_data.get_object_reference('Airlines', 'email_template_airlines_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        
        ctx = {
            'default_model': 'registry',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'force_email': True
        }

        return {
            'type': 'ir.actions.act_window',
            'View_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

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
            res_partner = self.env['res.partner'].search([('name','=',record.name)])
            if record.state == 'confir' and res_count <= 0:
                values = {
                    'name': record.name,
                    'image': record.image,
                    'email': record.email,
                    'website': record.website,
                    'phone': record.phone_central,
                    'street': record.origin,
                    'company_type': 'company'
                }
                res.create(values)
                self.sending_data_airlines_affiliates()
            elif res_count > 0:
                res = res_partner
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
                    'name': record.name,
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
            res_affiliates = self.env['airlines.affiliates'].search([('name', '=', record.name)])
            values = {
                'name': record.name,
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
                api_get = requests.get(f'http://api.aviationstack.com/v1/airlines?airline_name={record.name}&access_key=83d3c5d1cb2c1a010d3e2c375639bc0a')
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
            except requests.exceptions.ConnectionError:
                raise UserError('En estos momentos no podemos solucionar su requerimiento compruebe su conexion a internet')

    # def print_report(self):
        # report_action
        #return self.env.ref('Airlines.action_report_airlines_registry').report_action(self)


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



