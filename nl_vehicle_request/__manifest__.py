# -*- coding: utf-8 -*-

{
    'name': 'Vehicle Request',
    'version': '13.0.1',
    'category': 'Human Resources',
    'summary': 'Manage Vehicle Requests From Employee',
    'description': """
Vehicle Request
===============
This module is used for manage vehicle requests from employee.
This module also checking the vehicle availability at the requested time slot.


For any doubt or query email us at info@netlinks.af
""",
    'images': [],
    'author': 'NETLINKS LTD',
    'website': 'www.netlinks.af',
    'support': 'info@netlinks.af',
    'license': '',
    'price': '',
    'currency': '',
    'depends': ['base', 'fleet', 'nl_employee'],
    'data': [
        'data/data.xml',
        'data/email_template.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/employee_fleet_view.xml',
        'report/vehicle_reservation_slip.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
