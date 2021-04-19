
# -*- coding: utf-8 -*-
###############################################################################
#
#    jeffery CHEN fan<jeffery9@gmail.com>
#
#    Copyright (c) All rights reserved:
#        (c) 2017  TM_FULLNAME
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses
#    
#    Odoo and OpenERP is trademark of Odoo S.A.
#
###############################################################################
{
    'name': 'Airlines',
    'summary': 'Modulo para empresas de aerolineas',
    'version': '1.5',
    'description': """
        Modulo de practica y aprendizaje con logica de gestion
        de aerolineas 
    """,
    'author': 'LAngel Cartaya',
    'website': 'http:/',
    'license': '',
    'category': 'Uncategorized',
    'depends': ['base','account'],
    'data': [
        'wizard/report_registry_view.xml',
        'wizard/report_today_flight_view.xml',
        'wizard/file_extract_data_xlsx_view.xml',
        'views/registry_view.xml',
        'views/airlines_view.xml',
        'views/flights_view.xml',
        'views/account_info_flight_view.xml',
        'report/report_registry.xml',
        'security/security_view.xml',
    ],
}
