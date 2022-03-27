
import base64
from dateutil.relativedelta import relativedelta
from odoo import SUPERUSER_ID, http
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment as Home
from odoo.http import request
from werkzeug.exceptions import NotFound
from odoo.addons.website.controllers.main import Website


class EnhanceWebsite(Website):
    """ Enhance website on publishe """
    
    @http.route()
    def publish(self, id, object):
        Model = request.env[object]
        record = Model.browse(int(id))
        res = super().publish(id, object)
        if Model == request.env['hr.job.announcement'] and res:
            record.job_id.is_published = True
        return res


class WebsiteHrJobAnnouncement(Home):

    def jobs(self, country=None, department=None, office_id=None, **kwargs):
        raise NotFound()

    def jobs_detail(self, job, **kwargs):
        raise NotFound()

    def jobs_add(self, **kwargs):
        raise NotFound()

    def jobs_apply(self, job, **kwargs):
        raise NotFound()

    def _get_applicant_files_fields(self):
        """A Helper Method to get the applicants's File fields."""
        return ['candidate-resume']

    @http.route('''/jobs/announcements/detail/<model("hr.job.announcement"):job>''', type='http', auth="public", website=True, sitemap=True)
    def jobs_announcement_detail(self, job, **kwargs):
        if not job.can_access_from_current_website():
            raise NotFound()
        return request.render("nl_recruitment.announcement_detail", {
            'job': job,
            'main_object': job,
        })
    
    @http.route('''/jobs/announcements/apply/<model("hr.job.announcement"):job>''', type='http', auth="public", website=True, sitemap=True)
    def jobs_announcement_apply(self, job, **kwargs):
        if not job.can_access_from_current_website():
            raise NotFound()
        error = {}
        default = {}
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        applicant_1 = request.env['hr.applicant'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id)
        ], limit=1, order='create_date desc')
        countries = env['res.country'].sudo().search([])
        states = env['res.country.state'].sudo().search([])

        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('website_hr_recruitment_error')
            default = request.session.pop('website_hr_recruitment_default')

        companies = request.env['res.company'].sudo().search([])
        return request.render("nl_recruitment.announcement_application",{
            'applicant': applicant_1,
            'job': job,
            'error': error,
            'default': default,
            'countries': countries,
            'states': states,
            'companies': companies,
            'partner': request.env['res.users'].sudo().browse(request.uid).partner_id,
        })

    
    @http.route('/jobs/thankyou', methods=['POST'], type='http', auth="public", website=True)
    def jobs_thankyou(self, **kwargs):
        """
        A Method for rendering thankyou template after applying for the job.

        Args:
            kwargs: The second parameter to get the details of the job applicant.

        Returns:
            It renders the template & creates a record for job
            application also attaches the applicant's attachment to the object.
        """
        env = request.env(user=SUPERUSER_ID)
        gen_list = []
        gen_list_experience = []
        edu_rec1 = list(kwargs.get('education_generalized1').split(','))
        edu_rec2 = list(kwargs.get('education_generalized2').split(','))
        edu_rec3 = list(kwargs.get('education_generalized3').split(','))
        edu_rec4 = list(kwargs.get('education_generalized4').split(','))
        edu_rec5 = list(kwargs.get('education_generalized5').split(','))

        experience_generalized1 = list(kwargs.get('experience_generalized1').split(','))
        experience_generalized2 = list(kwargs.get('experience_generalized2').split(','))
        experience_generalized3 = list(kwargs.get('experience_generalized3').split(','))
        experience_generalized4 = list(kwargs.get('experience_generalized4').split(','))
        experience_generalized5 = list(kwargs.get('experience_generalized5').split(','))
    
        for i in range(len(edu_rec1)):
            if edu_rec4[i]:
                gen_list.append((0, 0, {
                    'start_year': edu_rec1[i],
                    'completion_year': edu_rec2[i],
                    'degree': edu_rec3[i],
                    'specialization': edu_rec4[i],
                    'university': edu_rec5[i]
                }))
        for main_list in range(len(experience_generalized4)):
            total_year = 0.0
            if experience_generalized2[main_list]:
                gen_list_experience.append((0, 0, {
                    'job_title': experience_generalized1[main_list],
                    'company': experience_generalized2[main_list],
                    'start_date': experience_generalized3[main_list] if experience_generalized3[main_list] else False,
                    'end_date': experience_generalized4[main_list] if experience_generalized4[main_list] else False,
                    'is_current': experience_generalized5[main_list]
                }))
        del gen_list_experience[0]
        del gen_list[0]

        job_announcement_id = request.env['hr.job.announcement'].sudo().search([('id','=',int(kwargs.get('job_id')))])
        country =  env['res.country'].sudo().browse(int(kwargs.get('nationality')))

        vals = {
            'job_announcement_id': int(kwargs.get('job_id')),
            'job_id': job_announcement_id.job_id.id,
            'name': kwargs.get('first_name') + ' ' + kwargs.get('last_name'),
            'father_name': kwargs.get('father_name'),
            'dob': kwargs.get('date_of_birth'),
            'gender': kwargs.get('gender'),
            'partner_mobile': kwargs.get('phone_number'),
            'email': kwargs.get('email'),
            'highest_qualification': kwargs.get('highest_qualification'),
            'nationality': country.name or '' ,
            'salary_grade': job_announcement_id.salary_grade.id,
            'salary_step': job_announcement_id.salary_step.id,
            'department_id': job_announcement_id.department_id.id,
            'unit_id': job_announcement_id.unit_id.id,
            'employment_type': job_announcement_id.employment_type,
        }
        
        if len(gen_list_experience) >= 1 and gen_list_experience[0][2].get('job_title'):
            vals.update({
                'experience_ids': gen_list_experience,
            })
        if len(gen_list) >= 1:
            vals.update({
                'qualification_ids': gen_list
            })
        result = request.env['hr.applicant'].sudo().create(vals)
        
        total_years_of_experience = 0.0
        years=0
        for item in result.experience_ids:
            end_date = item.end_date if item.end_date else result.application_date
            difference = relativedelta(item.start_date, end_date)
            difference_in_years = (difference.years * -12) + (difference.months * -1)
            years = years + difference_in_years
        total_years_of_experience = years / 12
        quilified_stage_id = request.env['hr.recruitment.stage'].sudo().search([('state_mode', '=', 'qualified')],limit=1)
        not_qualified_stage_id = request.env['hr.recruitment.stage'].sudo().search([('state_mode', '=', 'not_qualified')],limit=1)

        to_update_id = False
        if result.job_announcement_id.qualifications_criteria_ids:
            qualifications = { rec.qualification: {'exper': rec.years_of_experience } for rec in  result.job_announcement_id.qualifications_criteria_ids}
            if result.highest_qualification in qualifications:
                if total_years_of_experience >= qualifications.get(result.highest_qualification).get('exper'):
                    to_update_id = quilified_stage_id.id if quilified_stage_id else False
                else:
                    to_update_id = not_qualified_stage_id.id if not_qualified_stage_id else False
            else:
                if int(result.highest_qualification) > int(min(qualifications)):
                    to_update_id = quilified_stage_id.id if quilified_stage_id else False
                else:
                    to_update_id = not_qualified_stage_id.id if not_qualified_stage_id else False 

        else:
            to_update_id = quilified_stage_id.id if quilified_stage_id else False
        
        result.with_context(ignore_applicant_constrains=True).update({'stage_id': to_update_id, 'total_years_of_experience': total_years_of_experience})

        for field_name in self._get_applicant_files_fields():
            if kwargs[field_name]:
                attachment_vals = {
                    'name': kwargs[field_name].filename,
                    'res_name': vals['name'],
                    'res_model': 'hr.applicant',
                    'res_id': result.id,
                    'datas': base64.encodestring(kwargs[field_name].read()),
                    # 'datas_fname': kwargs[field_name].filename,
                }
                env['ir.attachment'].sudo().create(attachment_vals)
        return request.render("nl_recruitment.thankyou", {
            'company_id': request.env.company,
        })
