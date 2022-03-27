# -*- coding: utf-8 -*-

{
    'name': 'Employees',
    'version': '13.0.1',
    'category': 'Human Resources',
    'summary': 'Centralize employee information',
    'description': """
Human Resources
===============
Centralize employee information.


For any doubt or query email us at info@netlinks.af
""",
    'images': [],
    'author': 'NETLINKS LTD',
    'website': 'www.netlinks.af',
    'support': 'info@netlinks.af',
    'license': '',
    'price': '',
    'currency': '',
    'depends': ['hr','mail','website','report_xlsx', 'nl_master', 'hr_employee_entry_checklist'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/certificate_report.xml',
        'report/report_header.xml',
        'report/report_footer.xml',
        'report/certificate_template.xml',
        'report/confidentiality_agreement.xml',
        'report/conflict_of_interest.xml',
        'report/acknoledgement_letter.xml',
        'report/reference_check.xml',
        'views/reference_web.xml',
        'views/employee_views.xml',
        'views/hr_unit.xml',
        'views/cost_center.xml',
        'views/inherit_views.xml',
        'views/bank_views.xml',
        'wizard/excel_report.xml',
        'wizard/employment_certificate_signatory.xml',
        'data/timesheet_email_template.xml',
        'data/data.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
