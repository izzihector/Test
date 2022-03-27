# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'HR Documentation',
    'version': '13.0.1',
    'category': 'Human Resources',
    'summary': 'HR Documentation',
    'description': """
HR Documentation
================


For any doubt or query email us at contact@serpentcs.com
""",
    'images': [],
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'support': 'contact@serpentcs.com',
    'license': '',
    'price': '',
    'currency': '',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'report/report_view.xml',
        'views/hr_doc_view.xml',
        'report/report_document_view.xml',
        'wizard/hr_doc_view.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
