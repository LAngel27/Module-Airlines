# -*- coding: utf-8 -*-
from odoo import models,fields,api


class TaskWizard(models.TransientModel):
    _name = 'report.registry'


    

    ''' workbook = xlwt.Workbook(encoding="utf-8")
    style_one = xlwt.easyxf('alignment: horiz centre')
    sheet = workbook.add_sheet("Servicios de empleados")
    today = datetime.datetime.now().date()
    file_name = "Servicios de empleados " + str(today)
    sheet.write(0, 0, 'ID')
    sheet.write(0, 1, 'Referencia del Contrato')
    sheet.write(0, 2, 'hr_discount')
    sheet.write(0, 3, 'cumplimiento_meta')
    sheet.write(0, 4, 'evaluacion_desemp')
    sheet.write(0, 5, 'comisiones')
    sheet.write(0, 6, 'horas_extras')
    for x, l in zip(range(1, 11), lt):
        sheet.write(x, 0, l, style_one)
    workbook.save('./archivos/ejemplos.xlsx')
    '''