from odoo import fields,models,api
from odoo.exceptions import UserError
from  base64 import b64decode
import tempfile
import pandas as pd



class RegistryElectronic(models.TransientModel):
    _name = 'registry.electronic'
    

    name = fields.Char(string='Nombre')
    country_origin = fields.Char(string='Origen(sede)')
    iata = fields.Char(string='IATA')
    oaci = fields.Char(strng='OACI')
    phone_central = fields.Char(string='Central telefonica')
    file_xlsx = fields.Binary(help='debe ser un archivo tipo .xls o .xlsx', copy=False)


    def document_analyzer_xlsx_and_save_data(self):
        decode = b64decode(self.file_xlsx)
        file = f'{tempfile.gettempdir()}/file.xls'
        f = open(file, 'wb')
        f.write(decode)
        f.seek(0)
        f.close()

        headers = ['Nombre', 'Director', 'IATA', 'OACI', 'Sede', 'telefono']
        file_excel = open(file,'rb')
        df = pd.read_excel(file_excel,header=0)
        df_columms = df.columns.values
        cols = [line for line in df_columms]
        values = []
        datas = []
        res = self.env['res.partner']
        for header,col in zip(headers,cols):
            if header == col:
                values.append(col)
            else:
                raise UserError(f'El archivo debe contener los siguientes encabezados {header}')
    
        for index,line in df.iterrows() :
            vals = {
                'name': line['Nombre'],
                'street': line['Sede'],
                'vat': line['IATA'],
                'phone': line['telefono']
            }

            res.create(vals)
            datas.append(vals)
        
        file_excel.close()
        

