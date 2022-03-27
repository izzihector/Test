# -*- coding: utf-8 -*-

{
    'name': 'Employee Separation',
    'version': '13.0.1',
    'category': 'Human Resources',
    'summary': 'Employee Separation',
    'description': """
Employee Separation Management
==============================
This Module is used to manage Employee Separation
-> One can manage the notice period of the employee
-> One can print the separation documents like relieving letter,
   experience letter and recommendation letter.
-> Once the employee is relieved it will deactivate the employee


For any doubt or query email us at info@netlinks.af
""",
    'images': [],
    'author': 'NETLINKS LTD',
    'website': 'www.netlinks.af',
    'support': 'info@netlinks.af',
    'license': '',
    'price': '',
    'currency': '',
    'depends': ['hr_doc', 'nl_employee', 'nl_contract',],
    'data': [
        'security/hr_separation_security.xml',
        'security/ir.model.access.csv',
        'data/data_recom_exp_letter.xml',
        'data/data_relieve.xml',
        'data/cron.xml',
        'views/hr_separation_view.xml',
        'views/exit_interview_form.xml',
        'report/certificate_report.xml',
        'report/report_header.xml',
        'report/report_footer.xml',
        'report/certificate_template.xml',
        'report/separation_report.xml',
        'views/hr_separation_sequence.xml',
        'views/hr_view.xml',
        'data/email_template.xml',
        'wizard/hr_doc_view.xml',
        'views/exit_interview.xml',
        'report/employee_termination_template.xml',
        'report/exit_interview_form_template.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
