# -*- coding: utf-8 -*-
from odoo import models,fields,api

class Airlines(models.Model):
    _name = 'airlines.affiliates'


    company_name = fields.Char(string='nombre')
    direct = fields.Char(string="Director")
    phone = fields.Char(string="telefono")
    image = fields.Binary()
    email = fields.Char(string="email")
    