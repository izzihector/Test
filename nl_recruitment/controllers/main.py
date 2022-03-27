# -*- coding: utf-8 -*-

import base64
import werkzeug.utils
from datetime import datetime
from dateutil.relativedelta import relativedelta
import odoo.addons.website_sale.controllers.main
from odoo import SUPERUSER_ID, http
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment as Home
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request


class WebsiteHrRecruitment(Home):
    """This class is defined to enhance HR Recruitment portal."""

    # @http.route('/jobs/apply/<model("hr.job"):job>', type='http',
    #             auth="public", website=True)
    # def jobs_apply(self, job, **kwargs):
    #     """
    #     A Method for the users to be able to apply for job.

    #     Args:
    #         job: The first parameter to fetch the job position.
    #         kwargs: The second parameter to get the details of
    #         the job applicant.

    #     Returns:
    #         It renders the template & creates a record for job application.
    #     """
    #     error = {}
    #     default = {}
    #     env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
    #     applicant_1 = request.env['hr.applicant'].sudo().search([
    #         ('partner_id', '=', request.env.user.partner_id.id)
    #     ], limit=1, order='create_date desc')
    #     countries = env['res.country'].sudo().search([])
    #     states = env['res.country.state'].sudo().search([])

    #     if 'website_hr_recruitment_error' in request.session:
    #         error = request.session.pop('website_hr_recruitment_error')
    #         default = request.session.pop('website_hr_recruitment_default')

    #     companies = request.env['res.company'].sudo().search([])
    #     return request.render("nl_recruitment.supplier_registration",{
    #                 'applicant': applicant_1,
    #         'job': job,
    #         'error': error,
    #         'default': default,
    #         'countries': countries,
    #         'states': states,
    #         'companies': companies,
    #         'partner': request.env['res.users'].sudo().browse(request.uid).partner_id,
    #     })

    # def _get_applicant_files_fields(self):
    #     """A Helper Method to get the applicants's File fields."""
    #     return ['candidate-resume']

    # def _get_residential_address(self, kwargs):
    #     """A Helper Method to get the applicants's residential address."""
    #     address = {
    #         'name': kwargs.get('firstname'),
    #         'street': kwargs.get('street'),
    #         'street2': kwargs.get('street2') or '',
    #         'city': kwargs.get('city'),
    #         'zip': kwargs.get('zip'),
    #         'state_id': kwargs.get('state_id'),
    #         'country_id': kwargs.get('country_id'),
    #         'mobile': kwargs.get('partner_mobile'),
    #         'email': kwargs.get('email_from'),
    #         'customer': False,
    #     }
    #     return address

    # def _format_date(self, date):
    #     """A Helper Method to get the formated value of the date."""
    #     if date:
    #         return datetime.strptime(date, "%m/%d/%Y").isoformat(' ')
    #     return False


    # @http.route('/jobs/thankyou', methods=['POST'], type='http', auth="public", website=True)
    # def jobs_thankyou(self, **kwargs):
    #     """
    #     A Method for rendering thankyou template after applying for the job.

    #     Args:
    #         kwargs: The second parameter to get the details of the job applicant.

    #     Returns:
    #         It renders the template & creates a record for job
    #         application also attaches the applicant's attachment to the object.
    #     """
    #     env = request.env(user=SUPERUSER_ID)
    #     gen_list = []
    #     gen_list_experience = []
    #     edu_rec1 = list(kwargs.get('education_generalized1').split(','))
    #     edu_rec2 = list(kwargs.get('education_generalized2').split(','))
    #     edu_rec3 = list(kwargs.get('education_generalized3').split(','))
    #     edu_rec4 = list(kwargs.get('education_generalized4').split(','))
    #     edu_rec5 = list(kwargs.get('education_generalized5').split(','))
      




    #     experience_generalized1 = list(kwargs.get('experience_generalized1').split(','))
    #     experience_generalized2 = list(kwargs.get('experience_generalized2').split(','))
    #     experience_generalized3 = list(kwargs.get('experience_generalized3').split(','))
    #     experience_generalized4 = list(kwargs.get('experience_generalized4').split(','))
       


    #     for i in range(len(edu_rec1)):
    #         if edu_rec4[i]:
    #             gen_list.append((0, 0, {
    #                 'start_year': edu_rec1[i],
    #                 'completion_year': edu_rec2[i],
    #                 'degree': edu_rec3[i],
    #                 'specialization': edu_rec4[i],
    #                 'university': edu_rec5[i]
    #             }))
    #     for main_list in range(len(experience_generalized4)):
    #         total_year = 0.0
    #         if experience_generalized2[main_list]:
    #             gen_list_experience.append((0, 0, {
    #                 'job_title': experience_generalized1[main_list],
    #                 'company': experience_generalized2[main_list],
    #                 'start_date': experience_generalized3[main_list],
    #                 'end_date': experience_generalized4[main_list]
    #             }))
    #     print("Expereince details")
    #     del gen_list_experience[0]
    #     print(gen_list_experience)
    #     print("Education details")
    #     del gen_list[0]
    #     print(gen_list)
               
        
    #     job_id = request.env['hr.job'].sudo().search([('id','=',int(kwargs.get('job_id')))])
    #     country =  env['res.country'].sudo().browse(int(kwargs.get('nationality')))

    #     vals = {
    #         'job_id': int(kwargs.get('job_id')),
    #         'name': kwargs.get('first_name') + ' ' + kwargs.get('last_name'),
    #         'father_name': kwargs.get('father_name'),
    #         'dob': kwargs.get('date_of_birth'),
    #         'gender': kwargs.get('gender'),
    #         # 'marital_status': kwargs.get('marital'),
    #         # 'current_address': kwargs.get('current_addr'),
    #         # 'permanent_address': kwargs.get('permanent_addr'),
    #         'partner_mobile': kwargs.get('phone_number'),
    #         'email_from': kwargs.get('email'),
    #         'highest_qualification': kwargs.get('highest_qualification'),
    #         'nationality': country.name or '' ,
    #         # 'passport': kwargs.get('passport-applicant'),
    #         # 'passport_expiry_date': kwargs.get('passport-expiry'),
    #         # 'no_of_child': kwargs.get('children-applicant')
    #     }
        
    #     if len(gen_list_experience) >= 1 and gen_list_experience[0][2].get('job_title'):
    #         print("askl;djflasdjfl;kasjflk;asj")
    #         vals.update({
    #             'experience_ids': gen_list_experience,
    #         })
    #     if len(gen_list) >= 1:
    #         vals.update({
    #             'qualification_ids': gen_list
    #         })
        
    #     result = request.env['hr.applicant'].sudo().create(vals)
        
    #     total_years_of_experience = 0.0
    #     years=0
    #     for item in result.experience_ids:
    #         difference = relativedelta(item.start_date, item.end_date)
    #         print(difference)
    #         difference_in_years = (difference.years * -12) + (difference.months * -1)
            
    #         years = years + difference_in_years
    #     total_years_of_experience = years / 12
    #     quilified_stage_id = request.env['hr.recruitment.stage'].sudo().search([('qualified_stage','=',True)],limit=1)
    #     not_qualified_stage_id = request.env['hr.recruitment.stage'].sudo().search([('not_qualified_stage','=',True)],limit=1)

    #     if result.job_id.qualifications_criteria_ids:
    #         for item in result.job_id.qualifications_criteria_ids:
    #             print(item.qualification)
    #             if item.qualification == result.highest_qualification:
    #                 if total_years_of_experience>= item.years_of_experience:
    #                     result.update({'stage_id':quilified_stage_id.id,'total_years_of_experience':total_years_of_experience})
    #                     break
    #                 else:
    #                     result.update({'stage_id':not_qualified_stage_id.id,'total_years_of_experience':total_years_of_experience})
    #             else:
    #                 result.update({'stage_id':not_qualified_stage_id.id,'total_years_of_experience':total_years_of_experience})
    #     else:
    #         result.update({'stage_id':quilified_stage_id.id, 'total_years_of_experience':total_years_of_experience})
            
    #     for field_name in self._get_applicant_files_fields():
    #         if kwargs[field_name]:
    #             attachment_vals = {
    #                 'name': kwargs[field_name].filename,
    #                 'res_name': vals['name'],
    #                 'res_model': 'hr.applicant',
    #                 'res_id': result.id,
    #                 'datas': base64.encodestring(kwargs[field_name].read()),
    #                 # 'datas_fname': kwargs[field_name].filename,
    #             }
    #             env['ir.attachment'].sudo().create(attachment_vals)
    #     return request.render("nl_recruitment.thankyou")


# class WebsiteInherit(odoo.addons.web.controllers.main.Home):
#     """This class is defined to enhance HR Recruitment portal."""

#     @http.route(['/post_resume'], type='http', auth="public", website=True)
#     def post_resume(self, **kwargs):
#         """A Method to post the resume."""
#         return request.render("job_portal.social_info", {'page_from': 'resume'})

#     @http.route(['/post_job'], type='http', auth="public", website=True)
#     def post_job(self, **kwargs):
#         """A Method for Posting the Job from website portal.

#         Args:
#             kwargs: The second parameter to get the details of
#             the job posting.

#         Returns:
#             It renders the posting job template & takes the process further.
#         """
#         if not request.session.uid:
#             return werkzeug.utils.redirect('/web/login', 303)
#         return request.render("job_portal.post_resume", {
#             'page_from': 'job',
#             'job_department': request.env['hr.department'].sudo().search([]),
#             'job_type': request.env['hr.job.type'].sudo().search([]),
#         })
