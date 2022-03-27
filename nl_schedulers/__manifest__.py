# -*- coding: utf-8 -*-
{
    'name': "NL-ERP Scheduled Actions",

    'summary': """
        All scheduled actions devleoped for the NETLINKS ERP system. Current version includes: (a) product templates scheduler for webkul.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "NETLINKS LTD",
    'website': "http://www.netlinks.af",

    'category': 'Uncategorized',
    'version': '0.1.1',

    'depends': ['base','hr_contract'],

    'data': [
        'data/product_template_scheduler_template.xml',
    ],

    'demo': [
    ],
}
