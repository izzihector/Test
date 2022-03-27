# -*- coding: utf-8 -*-

{
    'name': 'Payroll',
    'version': '13.0.1',
    'category': 'Human Resources/Payroll',
    'summary': 'Manage nl Payroll ',
    'description': """
Payroll
=======

For any doubt or query email us at info@netlinks.af
""",
    'images': [],
    'author': 'NETLINKS LTD',
    'website': 'www.netlinks.af',
    'support': 'info@netlinks.af',
    'license': '',
    'price': '',
    'currency': '',
    'depends': ['hr_payroll','report_xlsx','mail', 'nl_separation'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/mail_template_data.xml',
        'data/activities.xml',
        'views/employee_absent.xml',
        'views/employee_pending.xml',
        'views/hr_payslip_computation.xml',
        'views/hr_payslip_employee.xml',
        'views/hr_payslip_run.xml',
        'views/hr_payslip.xml',
        'views/manual_allowance_deduction.xml',
        'views/master_batch.xml',
        'views/payslip_portal.xml',
        'report/report_payslip_templates.xml',
        'report/payroll_report.xml',
        

    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
