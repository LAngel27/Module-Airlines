# -*- coding: utf-8 -*-
from odoo import models,fields,api


class TaskWizard(models.TransientModel):
    _name = 'report.registry'


    def print_report(self):
        return self.env.ref('Airlines.action_report_airlines_registry').report_action(self)

    
