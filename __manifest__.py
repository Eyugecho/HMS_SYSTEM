# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Droga Physioterapy',
    'version' : '1',
    'summary': 'Saco about odoo erp',
    'sequence': 1,
    'description': """
Droga tranning on Odoo Development
====================
This module is not for production purpose it is used for train some droga staffs on how to develop on Odoo ERP system. this is basic
tutorial do not contain all""",
    'category': 'Physio',
    'website': 'https://www.drogapharma.com',
    'depends' : ['base_setup','hr'],
    
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/share.xml',
        'views/services.xml',
        'views/contracts.xml',
        'views/medical_certifcate.xml',
        'views/prescription_pdf.xml',
        'views/employee_contract.xml',
        'views/clinicians.xml'
        
        ],
    'installable': True,
    'application': True,
}
