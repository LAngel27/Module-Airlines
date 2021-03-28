# -*- coding: utf-8 -*-
from odoo import models,fields,api
from odoo.exceptions import UserError

class AirRegistry(models.Model):
    _name = 'registry'
    _description = 'modelo de registro aereo'


    name = fields.Char(requierd=True,string='Nombre')
    street = fields.Char(required=True,string="Sede")
    director = fields.Char(required=True, string='Director')
    sub_director = fields.Char(string='Subdirector')
    image = fields.Binary(required=True,help='Asegurese que sea el logo de la empresa')    
    state = fields.Selection(
        string='status',
        selection=[('draft', 'Borrador'), ('veri', 'Verifique'), ('confir','Confirmado')],
        default='draft',
    )
    website = fields.Char(string='Website',help='coloque direccion url')
    email = fields.Char(string='Email')
    phone_central = fields.Char(string='Central telefonica', required=True)
    dni = fields.Char(string="OACI", required=True)
    category = fields.Many2one(
        string='Categoria',
        comodel_name='res.partner.category',
        ondelete='restrict',
    )
    document = fields.Binary(help='En formato pdf')
    description_privacy_policy = fields.Text(string='Politicas de privacidad')
    
    def continues(self):
        self.state = 'veri'
    
    def continues_veri(self):
        self.state = 'confir'
    

    @api.multi
    def unlink(self):
        for record in self:
            if record.state == 'confir':
                raise UserError('No se puede modificar un registro en estado confirmado')
        return super(AirRegistry, self).unlink()
    
    @api.multi
    def sending_data_to_the_partner_and_update(self):
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
                    'street': record.street,
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
                    'street': record.street,
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
                    'email': record.email,
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
                'email': record.email,
            }
            write = res_affiliates.write(values)
        return write
