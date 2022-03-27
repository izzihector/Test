# -*- coding: utf-8 -*-

{
    'name': 'Employee Skills',
    'version': '13.0.1',
    'category': 'Leave',
    'summary': 'Employee Skills',
    'description': """
Employee Skills
===============
This module manages the Skills of an Employee.


For any doubt or query email us at info@netlinks.af
""",
    'images': [],
    'author': 'NETLINKS LTD',
    'website': 'www.netlinks.af',
    'support': 'info@netlinks.af',
    'license': '',
    'price': '',
    'currency': '',
    'depends': ['nl_employee', 'hr_skills'],
    'data': [
        'security/ir.model.access.csv',
        'data/resume_type.xml',
        'views/hr_resume_view.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
