# -*- coding: utf-8 -*-
from odoo import models,fields,api

class Airlines(models.Model):
    _name = 'airlines.affiliates'
    _description = 'modelo para aerolineas afiliadas'


    company_name = fields.Char(string='nombre',readonly=True)
    direct = fields.Char(string="Director",readonly=True)
    phone = fields.Char(string="telefono",readonly=True)
    image = fields.Binary()
    email = fields.Char(string="email",readonly=True)