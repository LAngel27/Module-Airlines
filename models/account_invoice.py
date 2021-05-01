# -*- coding: utf-8 -*-
from odoo import fields,models,api
from odoo.exceptions import UserError

class AccountInherit(models.Model):
    _inherit = 'account.invoice'
    _description = 'herencia del modelo account para añadir funcionalidades y practica de la herencia'

    transport_id = fields.Many2one(comodel_name='registry', string='Transporte')

    
    @api.multi
    def confirm_buy_flight(self):
        for record in self:
            query = self.env['ticket.flight'].search([('airline', '=', record.transport_id.name)])
            if query:
                query.update({
                    'receivable': False
                })
                record.state = 'paid'
            else:
                raise UserError(f'No pudimos encontrar el registro enlazado con la factura Nro {record.sequence_number_next_prefix}')

    # def test(self):
    #     print('hello world')
    #     for record in self:
    #         for line in record.invoice_line_ids:
    #             print(line.id)
