from odoo import api, fields, models


class ReportTicket(models.TransientModel):
    _name = 'report.ticket'

    @api.multi
    def print_report(self):
        return self.env.ref('Airlines.action_report_ticket').report_action(self)

