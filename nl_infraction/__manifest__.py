# -*- coding: utf-8 -*-

{
    'name': 'Employee Infraction Management',
    'version': '13.0.1',
    'category': 'Human Resources',
    'summary': 'Employee Infraction Management',
    'description': """
Employee Infraction Management
==============================
Disciplinary/Warning - Action Management.


For any doubt or query email us at info@netlinks.af
""",
    'images': [],
    'author': 'NETLINKS LTD',
    'website': 'www.netlinks.af',
    'support': 'info@netlinks.af',
    'license': '',
    'price': '',
    'currency': '',
    'depends': ['nl_employee'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_infraction_security.xml',
        'data/infraction_sequence.xml',
        'wizard/action.xml',
        'data/hr_infraction.xml',
        'views/hr_infraction_view.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
