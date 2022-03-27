# -*- coding: utf-8 -*-

{
    'name': 'Employee Contract',
    'version': '13.0.1',
    'category': 'Human Resources',
    'summary': 'Add information on the employee form to manage contracts.',
    'description': """
Employees Contract
==================
This module manage employee contract.


For any doubt or query email us at info@netlinks.af
""",
    'images': [],
    'author': 'NETLINKS LTD',
    'website': 'www.netlinks.af',
    'support': 'info@netlinks.af',
    'license': '',
    'price': '',
    'currency': '',
    'depends': ['nl_employee', 'hr_contract','hr_payroll'],
    'data': [
        'security/security_view.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'wizard/extend_probation.xml',
        'wizard/update_contract.xml',
        'views/contract_view.xml',
        'views/menus.xml',
        'views/extend_contract_view.xml',
        'views/action_menu.xml',
        'report/report_footer.xml',
        'report/employment_contract_v1.xml',
        'data/schedular.xml',
        'data/email_template.xml',
        'views/assets.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
