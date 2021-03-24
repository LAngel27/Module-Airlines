# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo.exceptions import UserError


class AirRegistry(models.Model):
    _name = 'registry'


    name = fields.Char(requierd=True,string='Nombre')
    street = fields.Char(required=True,string="Sede")
    director = fields.Char(required=True, string='Director')
    sub_director = fields.Char(required=True,string='Subdirector')
    image = fields.Binary(required=True,help='Asegurese que sea el logo de la empresa')    
    state = fields.Selection(
        string='status',
        selection=[('draft', 'Borrador'), ('veri', 'Verifique'), ('confir','Confirmar')],
        default='draft',
    )
    website = fields.Char(string='Website',help='coloque direccion url')
    email = fields.Char(string="Email")
    phone_central = fields.Char(string="Central telefonica", required=True)
    dni = fields.Char(string="Licencia", required=True)
    category = fields.Many2one(
        string='Categoria',
        comodel_name='res.partner.category',
        ondelete='restrict',
    )
    boolean = fields.Boolean()

    
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

