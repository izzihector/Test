# -*- coding: utf-8 -*-

{
    'name': 'Leave management',
    'version': '13.0.1',
    'category': 'Leave',
    'summary': 'Employee Leave Management',
    'description': """
Employee Leave Management
==============================


For any doubt or query email us at info@netlinks.af
""",
    'images': [],
    'author': 'NETLINKS LTD',
    'website': 'www.netlinks.af',
    'support': 'info@netlinks.af',
    'license': '',
    'price': '',
    'currency': '',
    'depends': ['hr_holidays', 'nl_contract'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/email_template.xml',
        'data/data.xml',
        'views/hr_leave_view.xml',
        'views/hr_leave_allocation_view.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
