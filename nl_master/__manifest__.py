# -*- coding: utf-8 -*-
{
    'name': "nl_master",
    'version': '13.0.1',
    'summary': """
        Contain Master Data For SCA""",

    'description': """
         Contain Master Data For SCA
    """,

    'author': 'NETLINKS LTD',
    'website': 'www.netlinks.af',
    'support': 'info@netlinks.af',
    'category': 'Master',
    'license': '',
    'price': '',
    'currency': '',
    'application': True,
    'installable': True,
    'auto_install': False,

    'depends': ['base', 'resource'],

    'data': [
        'views/templates.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/late_hours_exception.xml',
        'views/att_logs.xml',
    ],
}
