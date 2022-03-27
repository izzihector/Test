# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError 
from datetime import datetime, date
import base64
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.addons.nl_master.helpers import master_data
from dateutil.relativedelta import relativedelta
from base64 import b64decode
class HrApplicant(models.Model):
    _inherit = 'hr.applicant'
    _order = 'total_years_of_experience desc'

    @api.constrains('test_passing_score')  # name of field
    def _validate_duration(self):
        for rec in self:   # to prevent from the singleton error 
            if rec.test_passing_score > 100 or rec.test_passing_score <0:    
                raise ValidationError(_('Test Score should be set from 0 to 100%'))
    
    @api.constrains('interview_passing_score')  # name of field
    def _validate_duration(self):
        for rec in self:   # to prevent from the singleton error 
            if rec.interview_passing_score > 100 or rec.interview_passing_score <0:    
                raise ValidationError(_('Interview Score should be set from 0 to 100%'))

    application_date = fields.Date(default=fields.Date.context_today)
    name = fields.Char("Applicant's Name", required=True, help="Applicant's Name")
    partner_name = fields.Char("Applicant's Name" , related="name", store=True)
    highest_qualification = fields.Selection([
        ('0','Illiterate'),
        ('1','Primary'),
        ('2','Grade 12'),
        ('3','Grade 14'),
        ('4','Bachelor'),
        ('5','Master'),
        ('6','Doctorate'),
    ],string="Highest Education")

    test_passing_score = fields.Float(
        string="Test Score"
    )

    interview_passing_score = fields.Float(
        string="Interview Score"
    )

    total_years_of_experience = fields.Float('Years of Experience', compute="_compute_total_experience")
    
    father_name = fields.Char(
        string="Father's Name"
    )
    tazkira_number = fields.Char(
        string="Tazkira Number"
    )
    passport = fields.Char(
        string="Passport Number"
    )
    passport_expiry_date = fields.Date(
        string="Passport Expiry Date"
    )
    current_address = fields.Text(
        string="Current Address"
    )
    permanent_address = fields.Text(
        string="Permanent Address"
    )
    start_year = fields.Char(
        string="Start Year"
    )
    experience_ids = fields.One2many(
        "experience.experience",
        'applicant_id',
        string="Experience"
    )
    qualification_ids = fields.One2many(
        "qualifications.qualifications",
        'applicant_id',
        string="Qualifications"
    )
    dob = fields.Date(
        string="Date of Birth",
        required=True
    )
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string="Gender")
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string="Marital status")
    no_of_child = fields.Char(
        string='Number of children'
    )
    is_blacklisted = fields.Boolean(
        string="Blacklisted"
    )

    nationality = fields.Char(
        string="Nationality (Country)"
    )
    email = fields.Char("Email", size=128, help="Applicant email", compute='_compute_partner_phone_email',
        inverse='_inverse_partner_email', store=True, copy=True)
    office_id = fields.Many2one("office", string="Employee Office", related="job_announcement_id.office_id")
    unit_id = fields.Many2one('hr.unit', string="Unit")
    salary_grade = fields.Many2one('salary.grade',string="Grade")
    salary_step = fields.Many2one('salary.step',string="Step")
    pension_amount = fields.Float(string='Pension', default=0.0)
    date_start = fields.Date(string="Starting Date")
    probation_period = fields.Selection([
        ('one_month','1 Month'),
        ('two_month','2 Month'),
        ('three_month','3 Month')
    ],string="Probation Period", related="job_announcement_id.probation_period")
    other_benifits = fields.Text(string="Other Benefits")
    employment_type = fields.Selection(master_data.EMPLOYEMENT_TYPE)
    recruitment_officer = fields.Many2one("res.users", related="job_announcement_id.recruitment_officer")

    # Other Fields
    total_shortlisting_score = fields.Float(
        compute="_compute_total_shortlisting_score",
        string="Shortlisting Average Score"
        )
    total_score_category = fields.Selection([
        ('poor', 'Poor'),
        ('below_exceptions', 'Below Expectations'),
        ('minor_shortfall', 'Minor Shortfall'),
        ('competent', 'Competent'),
        ('beyond_competent', 'Beyond Competent'),
        ], string="Index Category", compute="_compute_score_category")
    written_test_result = fields.Float(string="Written Test Score")
    interview_result = fields.Float(compute="_compute_total_interview_result", string="Interview Average Score")
    test_interview_average = fields.Float(compute="_compute_test_interview_average", string="Total Average of Test and Interview")

    stage_state_mode = fields.Selection(related="stage_id.state_mode")
    stage_state_sequence = fields.Integer(related="stage_id.sequence")
    old_stage_state_sequence = fields.Integer(default=0)
    score_ids = fields.One2many('hr.applicant.score', 'applicant_id', string="Panel Members Score")
    interview_score_line = fields.One2many('hr.applicant.interview.score', 'applicant_id', string="Panel Members Interview Score")
    va_reference = fields.Char(string="Reference", related="job_announcement_id.va_reference")
    medical_ids = fields.One2many('completed.pikaz.clearance', 'applicant_id')
    references_ids = fields.One2many(
            'employee.references',
            'applicant_id',
            string="References",
            groups="hr.group_hr_user",
    )
    attachment_id = fields.Many2one('ir.attachment', string="Offer Letter Attachment")
    sign_template_id = fields.Many2one('sign.template', string="Sign",copy=False)
    sign_request_ids = fields.Many2many('sign.request', string="Signature Requests",copy=False)
    sign_counts = fields.Integer(compute="_get_sign_counts")

    def _get_sign_counts(self): #enhcance this ----- faridoon
        sign_request_ids = self.env['sign.request'].search([('template_id','=',self.sign_template_id.id)])
        for item in self: 
            item.sign_request_ids = sign_request_ids
            if item.sign_request_ids.state == 'signed':
                self.message_post(body="The Offer letter has been signed.")
        self.sign_counts = len(sign_request_ids)

    def action_view_sign_requests(self):
        sign_request_id = self.mapped('sign_request_ids')
        self.ensure_one()
        request_item = sign_request_id.request_item_ids.filtered(lambda r: r.partner_id and r.partner_id.id == self.recruitment_officer.id)[:1]
        return {
            'name': sign_request_id.reference,
            'type': 'ir.actions.client',
            'tag': 'sign.Document',
            'context': {
                'id': sign_request_id.id,
                'token': sign_request_id.access_token,
                'sign_token': request_item.access_token if request_item and request_item.state == "sent" else None,
                'create_uid': sign_request_id.create_uid.id,
                'state': sign_request_id.state,
            },
        }

    def _compute_total_experience(self):
        years=0
        for rec in self:
            for item in rec.experience_ids:
                end_date = item.end_date if item.end_date else item.applicant_id.application_date
                difference = relativedelta(item.start_date, end_date)
                difference_in_years = (difference.years * -12) + (difference.months * -1)
                years = years + difference_in_years
            rec.total_years_of_experience = years / 12

    @api.constrains("dob")
    def _validate_dob(self):
        for rec in self:
            if rec.dob and (fields.Date.today().year - rec.dob.year) < 18:
                raise ValidationError(_("Age should be alteast 18 years."))

    def _compute_current_user(self):
        for rec in self:
            rec.is_current_user_recruitment_admin = True if self.env.user.has_group('hr_recruitment.group_hr_recruitment_user') else False

    is_current_user_recruitment_admin = fields.Boolean(compute="_compute_current_user", string="Is Admin User")


    @api.onchange("employment_type", "salary_grade", "salary_step")
    def _compute_total_salary(self):
        for rec in self:
            rec.salary_expected = False
            if rec.employment_type and rec.salary_grade and rec.salary_step:
                    rec.salary_expected = rec.salary_step.value

    @api.onchange("salary_expected", "employment_type")
    def _compute_pension(self):
        for rec in self:
            rec.pension_amount = False
            if rec.employment_type and rec.employment_type == 'open_ended':
                rec.pension_amount = (rec.salary_expected * 8.4) / 100
    assessment_summary = fields.Text()
    
    @api.onchange("stage_id")
    def validate_stages(self):
        for rec in self:
            if rec._origin:
                if rec.stage_state_sequence <= rec.old_stage_state_sequence and not self.env.user.has_group("hr_recruitment.group_hr_recruitment_manager"):
                    raise ValidationError(_("Backward staging is not allowed; Either promote or disqualify the applicant."))
                if rec.stage_state_sequence:
                    rec.old_stage_state_sequence = rec.stage_state_sequence - 1 
                else:
                    rec.old_stage_state_sequence = 0

            if rec.stage_id.state_mode not in ['disqualified', 'refused', 'blacklisted', 'none']:
                if rec.stage_id.sequence > 2 and not len(rec.score_ids) > 0:
                    raise ValidationError(_("Shortlising scores need to be configured for the applicant to proceed."))

                if rec.stage_id.sequence > 3 and not rec.written_test_result:
                    raise ValidationError(_("Written test scores need to be configured for the applicant to proceed."))

                if rec.stage_id.sequence > 4 and not len(rec.interview_score_line) > 0:
                    raise ValidationError(_("Interview results need to be configured for the applicant to proceed."))
                
                if rec.stage_id.sequence > 5: 
                    if not rec.references_ids or len(list(filter(lambda x: not x.checked, rec.references_ids))):
                        raise ValidationError(_("Before proceeding with the applicant's offer, make sure his/her references are checked and verified."))

    def _compute_total_shortlisting_score(self):
        for rec in self:
            pannel_members_count = len(rec.score_ids)
            rec.total_shortlisting_score = False
            if pannel_members_count != 0:
                rec.total_shortlisting_score = sum([int(x) for x in rec.score_ids.mapped('shortlisting_score')]) / pannel_members_count
            
    def _compute_total_interview_result(self):
        for rec in self:
            pannel_members_count = len(rec.interview_score_line)
            rec.interview_result = False
            if pannel_members_count != 0:
                rec.interview_result = (sum([int(x) for x in rec.interview_score_line.mapped('interview_score')]) / pannel_members_count) / 10
            
    def _compute_test_interview_average(self):
        for rec in self:
            rec.test_interview_average = (rec.written_test_result + rec.interview_result) / 2 
            
    @api.onchange("job_announcement_id")
    def cal_job_id(self):
        for rec in self:
            if rec.job_announcement_id:
                rec.job_id = rec.job_announcement_id.job_id

    @api.depends('total_shortlisting_score')
    def _compute_score_category(self):
        for rec in self:
            rec.total_score_category = master_data.SCORE_RANGE_DICT.get(str(int(rec.total_shortlisting_score)))
    
    @api.onchange('employment_type')
    def _onchange_salary(self):
        for rec in self:
            rec.salary_grade = False

    @api.onchange('salary_grade')
    def _onchange_salary_grade(self):
        for rec in self:
            rec.salary_step = False

    def _remove(self):
        self.env['hr.resume.line'].search([
            ('active', '!=', True)
        ]).unlink()


    def application_confirm_mail(self, applicant):
        user = self.env['res.users']
        from_mail = user.env.user.login
        from_mail = from_mail.encode('utf-8')
        
        to_mail = (applicant.email).encode('utf-8')

        email_template = self.env.ref(
            'nl_recruitment.email_application_confirm')

        para = """
            Thank you for your application; Your application has been received for the following vacancy: %s. Please note that due to the high number of applications we receive, 
            we will only be able to provide you with updates regarding the recruitment process in case you were shortlisted.
        """ % (applicant.job_announcement_id.job_id.name)

        body_html = """
            <![CDATA[<div style="font-family: 'Lucica Grande',
            Ubuntu, Arial, Verdana, sans-serif; font-size: 14px;
            color: rgb(34, 34, 34); background-color: #FFF; ">
            <p>Dear """+ applicant.name +""",</p>
            """+ para +"""
            <br/>
            <br/>
            <p>Best Regards,<br/>
            <p>Human Resources Unit<br /></p>
            <img src="/logo.png?company=%s" style="padding: 0px; margin: 0px; height: auto; width: 190px;margin-bottom: 13px" alt="%s"/>
            <p>Swedish Committee for Afghanistan<br /></p>
        """% (self.env.user.company_id.id, self.env.user.partner_id.company_id.name)

        if email_template:
            email_template.sudo().write({
                'body_html': body_html,
                'email_from': from_mail,
                'email_to': to_mail
            })
            email_template.send_mail(applicant.id, force_send=True)

    @api.model
    def create(self, vals):
        resource = super(HrApplicant, self).create(vals)
        followers = [partner.id for partner in resource.job_announcement_id.panel_members.mapped('partner_id')]
        resource.application_confirm_mail(resource)
        subtype_ids = self.env['mail.message.subtype'].search(
            [('res_model', '=', 'hr.applicant')]).ids
        resource.message_subscribe(
            partner_ids=followers,
            subtype_ids=subtype_ids)
        return resource

    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            
            if applicant.stage_id.state_mode != 'offer_signed':
                raise ValidationError(_("Employee can only be created from the state with the Proposal Offer as state mode"))

            if not applicant.office_id:
                raise ValidationError(_("Please Add Employee Office for the Current Applicant First."))

            if not applicant.medical_ids or len(list(filter(lambda x: not x.checked, applicant.medical_ids))):
                raise ValidationError(_("In order to proceed with the contract issuance, make sure  medical examinations are cleared for the applicant."))

            contact_name = False

            # Manage Partner Details
            new_partner_id = applicant.partner_id
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.display_name
            else:
                if not applicant.name:
                    raise UserError(_('You must define a Contact Name for this applicant.'))
                    
                new_partner_id = self.env['res.partner'].sudo().create({
                    'is_company': False,
                    'name': applicant.name,
                    'email': applicant.email,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile,
                    'street': applicant.permanent_address
                })
                address_id = new_partner_id.address_get(['contact'])['contact']

            # Create User
            user = self.env['res.users'].sudo().create({
                'name': applicant.name,
                'login': applicant.name + str(applicant.id) + "@test.test",
                'sel_groups_1_9_10': '9',
                'partner_id': new_partner_id.id
                })

            # Custom code for netlinks-erp
            passport_expiry_date = ""
            if applicant.passport_expiry_date:
                passport_expiry_date = datetime.strftime(applicant.passport_expiry_date, '%Y-%m-%d')

            dob = datetime.strftime(applicant.dob, '%Y-%m-%d')
            regular_types = ['open_ended', 'casual_contract', 'fixed_term', 'project_based']
            fps_type = ['fps1_2', 'fps1']
            emp_type = False
            if  applicant.job_announcement_id.employment_type in regular_types:
                emp_type = 'regular'
            elif applicant.job_announcement_id.employment_type in fps_type:
                emp_type = 'field'

            if applicant.name or contact_name:
                employee = self.env['hr.employee'].sudo().create({
                    'name': applicant.name or contact_name,
                    'job_id': applicant.job_id.id or False,
                    'completed_pikaz_clearance': True,
                    'job_title': applicant.job_id.name,
                    'address_home_id': address_id,
                    'department_id': applicant.department_id.id or False,
                    'unit_id': applicant.unit_id.id or False,
                    'address_id': applicant.company_id and applicant.company_id.partner_id
                            and applicant.company_id.partner_id.id or False,
                    'work_email': applicant.department_id and applicant.department_id.company_id
                            and applicant.department_id.company_id.email or False,
                    'work_phone': applicant.department_id and applicant.department_id.company_id
                            and applicant.department_id.company_id.phone or False,

                    'personal_email': applicant.email_from or '',
                    'father_name': applicant.father_name or '',
                    'identification_id': applicant.tazkira_number or '',
                    'passport_id': applicant.passport or '',
                    'passport_expiry_date': passport_expiry_date or False,
                    'children': applicant.no_of_child or '',
                    'marital': applicant.marital_status or '',
                    'birthday': dob or False,
                    'join_date': datetime.strftime(datetime.now(), '%Y-%m-%d'),
                    'personal_mobile': applicant.partner_mobile,
                    'gender': applicant.gender,
                    'office_id': applicant.office_id.id or False,
                    'employee_type': emp_type,
                    'is_illiterate': True if applicant.highest_qualification == '0' else False,
                    'user_id': user.id
                    })

                applicant.write({'emp_id': employee.id})
                if applicant.job_announcement_id:
                    applicant.job_announcement_id.write({'no_of_hired_employee': applicant.job_announcement_id.no_of_hired_employee + 1})
                    applicant.job_announcement_id.message_post(
                        body=_('New Employee %s Hired') % applicant.name if applicant.name else applicant.name,
                        subtype_xmlid="hr_recruitment.mt_job_applicant_hired")

                self.env['employee.announcement.line'].create({
                    'job_announcement_id': applicant.job_announcement_id.id,
                    'employee_id': employee.id,
                    'hire_date': fields.Date.today()
                    })

                applicant.message_post_with_view(
                    'hr_recruitment.applicant_hired_template',
                    values={'applicant': applicant},
                    subtype_id=self.env.ref("hr_recruitment.mt_applicant_hired").id)

                #  Create Contract
                office_record = self.env['hr.contract.approver'].sudo().search([('office_id', '=', applicant.job_announcement_id.office_id.id)], limit=1)
                approver = office_record.user_ids[0]
                salary_grade_and_step = False
                if applicant.salary_grade and applicant.salary_step:
                    salary_grade_and_step = applicant.salary_grade.name + '-' + applicant.salary_step.name

                contract = self.env['hr.contract'].sudo().create({
                    'employee_id': employee.id,
                    'department_id': applicant.department_id.id or False,
                    'unit_id': applicant.unit_id.id or False,
                    'job_id': applicant.job_id.id or False,
                    'employment_type': applicant.employment_type,
                    'salary_grade': applicant.salary_grade.id or False,
                    'salary_step': applicant.salary_step.id or False,
                    'grade_and_step': salary_grade_and_step,
                    'contract_approver_user': approver.id,
                    'date_start': applicant.date_start if applicant.date_start else fields.Date.today(),
                    })

                contract.sudo().update_wage_and_contract_terms()
                contract.sudo().set_domain_to_salary_grade()
                contract.sudo().update_wage_in_contract_terms()
                contract.sudo().set_domain_to_salary_step()
                contract.sudo().calculate_pension()
                contract.sudo().calculate_tax()
                contract.sudo().onchange_cal_pension()

            # Custom code for sca
            education_line_type = self.sudo().env.ref('hr_skills.resume_type_education', raise_if_not_found=False)
            for qual in applicant.qualification_ids:
                education_vals = {
                    'date_start': qual.start_year,
                    'date_end': qual.completion_year,
                    'name': qual.degree,
                    'specialization': qual.specialization,
                    'description': qual.university,
                    'line_type_id': education_line_type and education_line_type.id,
                    'active': True,
                    'employee_id': employee.id
                    }
                self._remove()
                self.env['hr.resume.line'].sudo().create(education_vals)

            experience_line_type = self.env.ref('hr_skills.resume_type_experience', raise_if_not_found=False)
            for exp in applicant.experience_ids:
                experience_vals = {
                    'name': exp.job_title,
                    'description': exp.company,
                    'date_start': exp.start_date,
                    'date_end': exp.end_date,
                    'line_type_id': experience_line_type and experience_line_type.id,
                    'active': True,
                    'employee_id': employee.id
                    }
                self._remove()
                self.env['hr.resume.line'].sudo().create(experience_vals)

            for document in applicant.attachment_ids:
                attachment_vals = {
                    'name': document.datas,
                    'file_name': document.name,
                    'emp_id': employee.id
                    }
                self.env['employee.document'].sudo().create(attachment_vals)

            for reference in applicant.references_ids:
                reference.update({'empl_id': employee.id})
            for medical in applicant.medical_ids:
                medical.update({'pikaz_id': employee.id})

        self.activity_hr_manager()

        employee_action = self.sudo().env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        dict_act_window['context'] = {'form_view_initial_mode': 'edit'}
        dict_act_window['res_id'] = employee.id
        return dict_act_window


    def activity_hr_manager(self):
        """ Create Activity for HR Responsibles """
        note = _('A profile for %s has been created. Kindly proceed with further data entry and follow-up.') % (
            self.emp_id.name)

        users = []
        office = self.emp_id.office_id
        hr_contract_approver = self.env['hr.contract.approver'].sudo().search([('office_id', '=', office.id)], limit=1)
        users = set(hr_contract_approver.infraction_approver_ids)
        for login in users:
            self.emp_id.activity_schedule(
                'nl_recruitment.mail_recruitment_new_hired_notification',
                note=note,
                user_id=login.id or self.env.user.id)


    def disqualify_record(self):
        for rec in self:
            disqualfied_stage = self.env['hr.recruitment.stage'].search([('state_mode', '=', 'disqualified')], limit=1)
            if not disqualfied_stage:
                raise ValidationError(_("Could find any stage with the state mode equal to Disqualified."))
            rec.stage_id = disqualfied_stage.id


    def send_offer_letter(self):
        self.sign_request_ids.unlink()
        for applicant in self:
            if applicant.stage_id.state_mode != 'offer_proposal':
                raise ValidationError(_("You can only send offer letter from stage with the Offer Signed as state mode."))
            if  not applicant.date_start or not applicant.employment_type:
                    raise ValidationError(_("Please Fill Out  Starting Date and Employment Type Under Contract Section  Before Proceeding."))
            if not applicant.references_ids or len(list(filter(lambda x: not x.checked, applicant.references_ids))):
                raise ValidationError(_("Before proceeding with the applicant's offer, make sure his/her references are checked and verified."))

            attachment_id = self.env['ir.attachment'].sudo().search([('name','=',"Offer Letter - " + self.name)], limit=1)
        
            if not attachment_id:
                return self.env.ref(
                'nl_recruitment.action_print_offer_letter').report_action(self)
            self.attachment_id = attachment_id
            bytes = b64decode(self.attachment_id.datas, validate=True)

        # Perform a basic validation to make sure that the result is a valid PDF file
        # Be aware! The magic number (file signature) is not 100% reliable solution to validate PDF files
        # Moreover, if you get Base64 from an untrusted source, you must sanitize the PDF contents
            if bytes[0:4] != b'%PDF':
                raise ValidationError('Missing the PDF file signature')
            else:
                if not self.sign_template_id:
                    if attachment_id:
                        sign_template_id = self.env['sign.template'].sudo().create({
                                'attachment_id':attachment_id.id,
                                'name':'Offer Letter - ' + self.name,
                                'privacy':'invite'
                            })
                        manager_role_id = self.env['sign.item.role'].sudo().search([('name','=','Manager')], limit=1)
                        print(manager_role_id.name)
                        if not manager_role_id:
                            raise UserError(_('Please ask Administrator to create a role by the name of Manager in Sign Module.'))

                        hr_responsible_role_id = self.env['sign.item.role'].sudo().search([('name','=','HR Responsible')], limit=1)
                        print(hr_responsible_role_id.name)
                        if not hr_responsible_role_id:
                            raise UserError(_('Please ask Administrator to create a role by the name of HR Responsible in Sign Module.'))

                        sign_request_id = self.env['sign.send.request'].sudo().create({'template_id':sign_template_id.id,
                            'subject':'Offer Letter - ' + self.name,'filename':self.attachment_id.name})

                        sign_hr_reponsible = self.env['sign.item'].sudo().create({
                            'type_id':1,
                            'required':True,
                            'responsible_id':hr_responsible_role_id.id,
                            'name':'Signature',
                            'page':1,
                            'posX':0.060,
                            'posY':0.545,
                            'width':0.249,
                            'height':0.052,
                            'template_id':sign_template_id.id
                        })
                        sign_manager = self.env['sign.item'].sudo().create({
                            'type_id':1,
                            'required':True,
                            'responsible_id':manager_role_id.id,
                            'name':'Signature',
                            'page':1,
                            'posX':0.364,
                            'posY':0.545,
                            'width':0.246,
                            'height':0.052,
                            'template_id':sign_template_id.id
                        })
                        # signer_ids = self.env['sign.send.request.signer'].sudo().search([('sign_send_request_id','=',sign_request_id.id)])
                        # print(signer_ids)
                        # vals = {
                        #     'signer_ids':signer_ids,
                           
                        #     'message':'Please sign the offer letter.',
                        # }
                        self.sign_template_id = sign_template_id.id

                        action = self.env['ir.actions.act_window']._for_xml_id('sign.action_sign_send_request')
                        action["context"] = {
                                "active_id": self.sign_template_id.id,
                                "sign_directly_without_mail": False,
                                'subject':'Offer Letter - ' + self.name,
                                'resource_id':self.id,
                                'hide_send_button':True
                            }
                    return action                        
                    
                else:
                    action = self.env['ir.actions.act_window']._for_xml_id('sign.action_sign_send_request')
                    action["context"] = {
                                "active_id": self.sign_template_id.id,
                                "sign_directly_without_mail": False,
                                'subject':'Offer Letter - ' + self.name,
                                'resource_id':self.id,
                                'hide_send_button':True
                            }
                    return action
            # template = self.env.ref("nl_recruitment.email_employee_offer_letter")
            # template.attachment_ids = [(6, 0, [attachment_id.id])]
            # template_values = {
            #     'email_to': '${object.email_from|safe}',
            #     'email_cc': False,
            #     'auto_delete': False,
            #     'partner_to': False,
            #     'scheduled_date': False,
            # }
            # template.sudo().write(template_values)
            # template.send_mail(applicant.id, force_send=False)
            # template.attachment_ids = [(3, attachment_id.id)]
        

    def write(self, vals):
        context = dict(self._context) or {}
        if (len(vals) == 1 and not 'sign_request_ids' in vals) and not self.env.user.has_group('hr_recruitment.group_hr_recruitment_user') and not context.get('ignore_applicant_constrains', False):
            raise ValidationError(_("You are not allowed to edit applicant's records."))

        res =  super(HrApplicant, self).write(vals)
        if self.emp_id:
            for ref in self.references_ids:
                if not ref.empl_id:
                    ref.empl_id = self.emp_id
        return res


class Qualifications(models.Model):
    _name = "qualifications.qualifications"
    _description = 'Qualifications'

    start_year = fields.Datetime(
        string='Start Year'
    )
    completion_year = fields.Datetime(
        string='Completion Year'
    )
    degree_qualification = fields.Selection([
        ('0','Illiterate'),
        ('1','Primary'),
        ('2','Grade 12'),
        ('3','Grade 14'),
        ('4','Bachelor'),
        ('5','Master'),
        ('6','Doctorate'),
    ],string="Degree")
    degree = fields.Char(
        string='Degree Title'
    )
    specialization = fields.Char(
        string='Specialization'
    )
    university = fields.Char(
        string='University'
    )
    applicant_id = fields.Many2one(
        'hr.applicant'
    )

class Experience(models.Model):
    _name = "experience.experience"
    _description = 'Experience'

    job_title = fields.Char(
        string='Job Title'
    )
    company = fields.Char(
        string='Company'
    )
    start_date = fields.Date(
        string='Start Date'
    )
    end_date = fields.Date(
        string='End Date'
    )
    applicant_id = fields.Many2one(
        'hr.applicant'
    )
    is_current = fields.Boolean()

    @api.onchange('is_current')
    def validate_end_date(self):
        for rec in self:
            rec.end_date = False
    
class HrJobs(models.Model):
    _inherit = 'res.users'

    def write(self, vals):
        self.clear_caches()
        return super(HrJobs, self).write(vals)

    job_id = fields.Many2one('hr.job')
    office_ids = fields.Many2many('office',string="Allowed Office")
