# -*- coding: utf-8 -*-
from odoo import fields,models,api
from odoo.exceptions import UserError

class AccountInherit(models.Model):
    _inherit = 'account.invoice'
    _description = 'herencia del modelo account para añadir funcionalidades y practica de la herencia'

    transport_id = fields.Many2one('registry', string='Transporte')

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
                raise UserError(f'No pudimos encontrar el registro enlazado con la factura Nro {record.id}')

    @api.multi
    def get_report_ticket(self):
        return  {
            'type': 'ir.actions.act_window',
            'name': 'Boleto',
            'res_model': 'report.ticket',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('Airlines.report_ticket_for_view').id,
            'target': 'new'
        }


class AccountLineInherit(models.Model):
    _inherit = 'account.invoice.line'

    flight_id = fields.Many2one('flights.info', string='Vuelo')
