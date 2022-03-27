# -*- coding: utf-8 -*-

{
    'name': "nl_appraisal",
    'version': '13.0.1',
    'category': 'Human Resources',
    'summary': 'Employee Appraisal',
    'description': """
Human Resources
===============
Employee Appraisal


For any doubt or query email us at info@netlinks.af
""",
    'images': [],
    'author': 'NETLINKS LTD',
    'website': 'www.netlinks.af',
    'support': 'info@netlinks.af',
    'license': '',
    'price': '',
    'currency': '',
    'depends': ['base','mail','hr','nl_employee'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/templates.xml',
        'views/assets.xml',
        'views/hr_employee.xml',
        'views/appraisal_portal.xml',
        'views/appraisal_view.xml',
        'wizards/batch_appraisal_view.xml',
        'views/objectives_view.xml',
        'views/probation_appraisal.xml',
        'views/employee_appraisal_report.xml',
        'views/appraisal_pip.xml',
        'views/appraisal_pip_portal.xml',
        'views/employee_pip_report.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
