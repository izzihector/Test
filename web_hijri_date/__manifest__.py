# See LICENSE file for full copyright and licensing details.

{
    "name": "Web Hijri Calendar",
    "category": "Web",
    "license": "LGPL-3",
    "author": 'Serpent Consulting Services Pvt. Ltd.',
    "website": 'http://www.serpentcs.com',
    "description":"""Odoo Web Display Hijri Calendar.
        You will be able to see the two date fields.The first date field is the base
        date field for English date picker and the below one is for the Hijri date picker field.
        """,
    "version": "13.0.1.0.0",
    "depends": ['web'],
    'data': [
        'views/templates.xml',
    ],
    'qweb' : [
        "static/src/xml/*.xml",
    ],
    'images': ['static/description/HijriCal.png'],
    'auto_install': False,
    'installable': True,
    'application': True,
    'price': 99,
    'currency': 'EUR'
}
