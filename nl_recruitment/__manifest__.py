# -*- coding: utf-8 -*-

{
    'name': 'Recruitment',
    'version': '13.0.1',
    'category': 'website',
    'summary': 'Job Portal for Employer and Job Seeker.\
        Online recruitment portal online applicant job recruitment\
        website career page Online resume submission',
    'description': """
Employee Infraction Management
==============================
Job Portal for Employer and Job Seeker.
Online recruitment portal online applicant job recruitment
website career page Online resume submission

For any doubt or query email us at info@netlinks.af
""",
    'images': ['static/description/banner.jpg'],
    'author': 'NETLINKS LTD',
    'website': 'www.netlinks.af',
    'support': 'info@netlinks.af',
    'license': '',
    'price': '',
    'currency': '',
    'depends': ['base','website_hr_recruitment', 'nl_skills', 'nl_master','sign'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/hr_recruitment_stage.xml',
        'data/activity_log.xml',
        'data/email_template.xml',
        'wizards/applicant_score.xml',
        'wizards/applicant_interview_score.xml',
        'wizards/mail_wizard.xml',
        'wizards/applicant_interview_score.xml',
        'wizards/applicant_score.xml',
        'views/assets.xml',
        'views/post_resume_view.xml',
        'views/hr_applicant.xml',
        'views/hr_job_view.xml',
        'views/hr_recruitment_view.xml',
        'views/res_users_view.xml',
        'views/job_announcement.xml',
        'views/job_announcements_portal.xml',
        'report/offer_letter_template.xml',
        'report/committee_agreement.xml',
        'report/employment_committee_minutes.xml',
        'report/shortlisting_matrix.xml',
        'report/reference_check.xml',
        'wizards/hr_applicant_download.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
