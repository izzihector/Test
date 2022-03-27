# -*- coding: utf-8 -*-

{
    'name': 'Employee Attendance',
    'version': '13.0.1',
    'category': 'Human Resources',
    'summary': 'Employee Review Attendance information.',
    'description': """
Employees Attendance
====================
Employee Review Attendance information.


For any doubt or query email us at info@netlinks.af
""",
    'images': [],
    'author': 'NETLINKS LTD',
    'website': 'www.netlinks.af',
    'support': 'info@netlinks.af',
    'license': '',
    'price': '',
    'currency': '',
    'depends': ['hr_attendance'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/security.xml',
        # 'data/schedular.xml',
        'views/hr_attendance_view.xml',
        'views/attendance_portal.xml',
        # 'views/absent_employees_view.xml',
        # 'wizard/review_reason_wizard_view.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
