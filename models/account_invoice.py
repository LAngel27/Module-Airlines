# -*- coding: utf-8 -*-
from odoo import fields,models,api

class AccountInherit(models.Model):
    _inherit = 'account.invoice'
    _description = 'herencia del modelo account para añadir funcionalidades y practica de la herencia'

    transport_id = fields.Many2one(comodel_name='registry', string='Transporte')
