from odoo import fields, models, api
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.nl_master.helpers import master_data
from odoo.exceptions import ValidationError, AccessError
from odoo.tools.translate import _
from odoo.tools.translate import html_translate
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz

class JobAnnouncement(models.Model):
    _name = 'hr.job.announcement'
    _inherit = ['mail.thread','mail.activity.mixin','resource.mixin', 'website.seo.metadata', 'website.published.multi.mixin']
    _rec_name = "job_id"
    _description = "Job Announcements"
    
    _sql_constraints = [("unique_record", "unique(va_reference)", "A record with the same Reference number already exits.")]

    job_id = fields.Many2one("hr.job", required=True, tracking=True)
    job_poisition_in_dari = fields.Char("وظیفه", related="job_id.job_poisition_in_dari")
    application_ids = fields.One2many('hr.applicant', 'job_announcement_id', "Applications")
    application_count = fields.Integer(compute='_compute_application_count', string="Application Count")
    no_of_hired_employee = fields.Integer(string='Hired Employees', copy=False,
        help='Number of hired employees for this job position during recruitment phase.')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('recruit', 'Recruitment in Progress'),
        ('close', 'Recruitment Done'),
    ], string='Status', readonly=True, required=True, tracking=True, copy=False, default='draft', help="Set whether the recruitment process is open or closed for this job position.")
    all_application_count = fields.Integer(compute='_compute_all_application_count', string="All Application Count")
    new_application_count = fields.Integer(
        compute='_compute_new_application_count', string="New Application",
        help="Number of applications that are new in the flow (typically at first step of the flow)")
    user_id = fields.Many2one('res.users', "Recruiter", tracking=True)
    no_of_recruitment = fields.Integer(string='Number of Vacancies', copy=False,
        help='Number of new employees you expect to recruit.', default=1, tracking=True)
    vacancy_start_date = fields.Date("Announcement Date", required=True)
    vacancy_deadline = fields.Date("Closing Date", required=True)
    
    qualifications_criteria_ids = fields.One2many('selection.criteria','job_announcement_id')
    requires_travel = fields.Boolean(
        string="Requires  Travel"
    )
    color = fields.Integer("Color Index")
    department_id = fields.Many2one('hr.department', string='Department', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    unit_id = fields.Many2one('hr.unit', string="Unit")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    document_ids = fields.One2many('ir.attachment', compute='_compute_document_ids', string="Resumes")
    documents_count = fields.Integer(compute='_compute_document_ids', string="Resumes Count")
    recruitment_file_ids = fields.One2many('ir.attachment', compute='_compute_recruitment_file_ids', string="Documents")
    recruitment_file_count = fields.Integer(compute='_compute_recruitment_file_ids', string="Document Count")

    office_id = fields.Many2one("office", string="Duty Station", domain=lambda self: [("id", "in", [office.id for office in self.env.user.office_ids])], required=True, tracking=True)
    employment_type = fields.Selection(master_data.EMPLOYEMENT_TYPE, string="Contract Status", required=True)
    salary_grade = fields.Many2one('salary.grade',string="Grade", tracking=True)
    salary_step = fields.Many2one('salary.step',string="Step", tracking=True)
    recruitment_officer = fields.Many2one("res.users", required=True, tracking=True, string="Recruitment Manager/Unit Head")

    written_test_date  = fields.Datetime(tracking=True)
    interview_date  = fields.Datetime(tracking=True)
    panel_members = fields.Many2many('res.users', tracking=True)
    va_reference = fields.Char(required=True, string="Reference", tracking=True)
    notes = fields.Text()
    employee_announcement_line_ids = fields.One2many('employee.announcement.line', 'job_announcement_id', string='Hired Candidates', readonly=True)
    probation_period = fields.Selection([
        ('one_month','1 Month'),
        ('two_month','2 Month(s)'),
        ('three_month','3 Month(s)')
    ],string="Probation Period")
    announcement = fields.Selection([
        ('announcement','Announcement'),
        ('re_announcement','Re-Announcement'),
    ], default="announcement")
    announcement_type = fields.Selection([
        ('new','New Post'),
        ('replacement','Replacement')
    ], default='new')

    #     Following computed fields are used in Pivot view
    female_applicant = fields.Integer(string="Recruited Female")
    male_applicant = fields.Integer(string="Recruited Male")
    female_applicant_not_recruited = fields.Integer(string="Not Recruited Female")
    male_applicant_not_recruited = fields.Integer(string="Not Recruited Male")
    compute_gender = fields.Boolean(compute="compute_applicant_gender")


    def compute_applicant_gender(self):
        self.compute_gender = True
        for announcement in self.env['hr.job.announcement'].search([]):
            male = 0
            female = 0
            not_recruited_male = 0
            not_recruited_female = 0
            for applicant in announcement.application_ids:
                if applicant.gender:
                    if applicant.gender == 'male':
                        if applicant.emp_id:       
                            male = male + 1
                        else:
                            not_recruited_male += 1
                    if applicant.gender == 'female':
                        if applicant.emp_id:
                            female = female + 1
                        else:
                            not_recruited_female += 1
            announcement.sudo().male_applicant = male
            announcement.sudo().female_applicant = female
            announcement.sudo().female_applicant_not_recruited = not_recruited_female
            announcement.sudo().male_applicant_not_recruited = not_recruited_male

    def calculate_and_return_pivot_view(self):
        self.compute_applicant_gender()

        action = self.env["ir.actions.actions"]._for_xml_id("nl_recruitment.action_job_announcement_form")
        return action

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('male/female', 'Male/Female')
    ], string="Gender", required=True, default='male')
    def _get_date_as_utc(self, date):
        mytz = pytz.timezone(self._context.get('tz') or self.env.user.tz)
        display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(
            str(date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(mytz), "%Y-%m-%d %H:%M:%S")
        return datetime.strptime(display_date_result, "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")


    def written_test_invite(self, data):
        for rec in self:
            email_template = False
            email_template = self.env.ref(
                    'nl_recruitment.written_test_mail_check')
            names = ""
            body_html = data.get('body', False)
            if email_template:
                email_template.sudo().write({
                    'subject': data.get('subject'),
                    'body_html': body_html,
                    'attachment_ids': data.get('attachment_ids'),
                    })
                for mail in data.get('recipients'):
                    names = names + f"<li>{mail.name}</li>"
                    email_template.sudo().write({'email_to': mail.email})
                    email_template.send_mail(mail.id, force_send=False)
            body_html = f"""
                Invitation emails to attend the written test have been sent to the following candidates: <br/>
                <ul>
                    {names}
                </ul>
                Written test scheduled for {mail.job_announcement_id.written_test_date.strftime("%d/%m/%Y") if mail.job_announcement_id.written_test_date else ''}
            """
            rec.message_post( body=_(body_html))

    def interview_invite(self, data):
        for rec in self:
            email_template = False
            email_template = self.env.ref(
                    'nl_recruitment.interview_mail_check')
            names = ""
            body_html = data.get('body', False)
            if email_template:
                email_template.sudo().write({
                    'subject': data.get('subject'),
                    'body_html': body_html,
                    'attachment_ids': data.get('attachment_ids'),
                    })
                for mail in data.get('recipients'):
                    names = names + f"<li>{mail.name}</li>"
                    email_template.sudo().write({'email_to': mail.email})
                    email_template.send_mail(mail.id, force_send=False)

            body_html = f"""
                Invitation emails to attend the interview have been sent to the following candidates: <br/>
                <ul>
                    {names}
                </ul>
                Written test scheduled for {mail.job_announcement_id.interview_date.strftime("%d/%m/%Y") if mail.job_announcement_id.interview_date else ''}
            """
            rec.message_post( body=_(body_html))

    def action_open_download_attachment_wizard(self):
        for rec in self:
            action = self.env["ir.actions.actions"]._for_xml_id("nl_recruitment.action_open_hr_applicant_download_view")
            action.update({
                'context': {'default_job_announcement_id':rec.id}
            })
            return action


    @api.onchange('employment_type')
    def _onchange_salary(self):
        for rec in self:
            rec.salary_grade = False

    @api.onchange('salary_grade')
    def _onchange_salary_grade(self):
        for rec in self:
            rec.salary_step = False

    def _get_summary_default():
        return """<p><span style="-webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); box-sizing: border-box; color: rgb(103, 84, 98); font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-size: 14px; font-style: inherit; font-variant-caps: normal; font-variant-ligatures: normal; font-weight: inherit; letter-spacing: normal; margin: 0px; text-align: start; text-decoration-color: initial; text-decoration-style: initial; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px;" id="isPasted"><strong>Job Summary:</strong><strong>&nbsp;</strong></span></p><p>Consetetur
 sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et 
dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et
 justo duo dolores et ea rebum. Stet clita kasd gubergren.<strong><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;;-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(103, 84, 98); font-size: 10pt; margin: 0px;"><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; margin: 0px; font-style: inherit; font-weight: inherit;">&nbsp;</span></span></strong><br><br></p><p><strong><span style="-webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); box-sizing: border-box; color: rgb(103, 84, 98); font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-size: 14px; font-style: inherit; font-variant-caps: normal; font-variant-ligatures: normal; font-weight: inherit; letter-spacing: normal; margin: 0px; text-align: start; text-decoration-color: initial; text-decoration-style: initial; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px;"><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; margin: 0px; font-style: inherit; font-weight: inherit;">​<span style="-webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); box-sizing: border-box; color: rgb(103, 84, 98); font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-caps: normal; font-variant-ligatures: normal; font-weight: inherit; letter-spacing: normal; margin: 0px; text-align: start; text-decoration-color: initial; text-decoration-style: initial; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px;" id="isPasted"><strong>Duties &amp; Responsibilities:</strong><strong>&nbsp;</strong></span></span></span></strong></p><p><span style="font-size: 13px;">​Consetetur
 sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et 
dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et
 justo duo dolores et ea rebum. Stet clita kasd gubergren.</span></p><ul><li><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;" id="isPasted">t
 labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et
 accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no
 sea takimata sanctus.</span><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;">&nbsp;</span></li><li><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;;-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;" id="isPasted">t
 labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et
 accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no
 sea takimata sanctus.</span><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;;-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;">&nbsp;</span></li><li><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;;-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;;-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;" id="isPasted">t
 labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et
 accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no
 sea</span><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;;-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;"></span><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;;-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;;-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;">.</span><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;;-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;"></span></li></ul><p><strong id="isPasted"><span style="-webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); box-sizing: border-box; color: rgb(103, 84, 98); font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-size: 14px; font-style: inherit; font-variant-caps: normal; font-variant-ligatures: normal; font-weight: inherit; letter-spacing: normal; margin: 0px; text-align: start; text-decoration-color: initial; text-decoration-style: initial; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px;"><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; margin: 0px; font-style: inherit; font-weight: inherit;">Qualifications and Experience<span style="-webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); box-sizing: border-box; color: rgb(103, 84, 98); font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-caps: normal; font-variant-ligatures: normal; font-weight: inherit; letter-spacing: normal; margin: 0px; text-align: start; text-decoration-color: initial; text-decoration-style: initial; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px;"><strong>:</strong></span></span></span></strong></p><p><span style="font-size: 13px;">Consetetur
 sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et 
dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et
 justo duo dolores et ea rebum. Stet clita kasd gubergren</span><strong id="isPasted"><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(103, 84, 98); font-size: 10pt; margin: 0px;"><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; margin: 0px; font-style: inherit; font-weight: inherit;"><strong><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;;-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(103, 84, 98); font-size: 10pt; margin: 0px;">&nbsp;&nbsp;</span></strong></span></span></strong></p><ul><li style="font-size: 13px;">t
 labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et
 accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no
 sea takimata sanctus.&nbsp;</li><li style="font-size: 13px;">​t labore et 
dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et
 justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea 
takimata sanctus.&nbsp;</li><li style="font-size: 13px;">t labore et dolore 
magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo 
duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata 
sanctus.&nbsp;</li></ul><p><strong><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(121, 121, 121); font-size: 10pt; margin: 0px;-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(103, 84, 98); font-size: 10pt; margin: 0px;"><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; margin: 0px; font-style: inherit; font-weight: inherit;"><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(103, 84, 98); font-size: 10pt; margin: 0px;"><strong><strong id="isPasted"></strong></strong></span><strong><strong id="isPasted"><span style="-webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); box-sizing: border-box; color: rgb(103, 84, 98); font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-size: 14px; font-style: inherit; font-variant-caps: normal; font-variant-ligatures: normal; font-weight: inherit; letter-spacing: normal; margin: 0px; text-align: start; text-decoration-color: initial; text-decoration-style: initial; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px;"><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; margin: 0px; font-style: inherit; font-weight: inherit;">Submission Guidelines<span style="-webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); box-sizing: border-box; color: rgb(103, 84, 98); font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-caps: normal; font-variant-ligatures: normal; font-weight: inherit; letter-spacing: normal; margin: 0px; text-align: start; text-decoration-color: initial; text-decoration-style: initial; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px;"><strong>:</strong></span></span></span></strong></strong><span style="-webkit-font-smoothing: antialiased; box-sizing: border-box; font-family: &quot;Segoe UI&quot;, system-ui, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, sans-serif; font-style: inherit; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: inherit; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial; color: rgb(103, 84, 98); font-size: 10pt; margin: 0px;"><strong><strong id="isPasted"></strong></strong></span></span></span></strong></p><p><span style="font-size: 13px;">Consetetur
 sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et 
dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et
 justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea 
takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit 
amet, consetetur sadipscing elitr. &nbsp;&nbsp; <br></span></p>"""

    summary = fields.Html(string="Desciption", default=_get_summary_default())

    # def _get_default_website_description(self):
    #     default_description = self.env["ir.model.data"].xmlid_to_object("website_hr_recruitment.default_website_description")
    #     return (default_description._render() if default_description else "")

    # website_description = fields.Html('Website description', translate=html_translate, sanitize_attributes=False, default=_get_default_website_description, prefetch=False, sanitize_form=False)


    def notify_panel_members(self):
        for rec in self:
            
            note = _(
                """You have been added as a member of Evaluation Committee for the recruitment for the following position:
                   <br/>
                   Position: %s <br/>
                   Duty Station: %s <br/>
                   Department: %s <br/>
                   Unit: %s <br/>
                   Announcement Date: %s <br/>
                   Planned Written Test: %s <br/><br/>
                   You can access the recruitment record from your HRIS user.
                """) % (rec.job_id.name, rec.office_id.name, rec.department_id.name, rec.unit_id.name, rec.vacancy_start_date, rec.written_test_date)
            users = rec.panel_members - self.env['mail.activity'].search([('res_model', '=', 'hr.job.announcement'), ('res_id', '=', rec.id)]).mapped('user_id')
            if not users:
                raise ValidationError(_("No new member to notify."))
            for login in users:
                rec.activity_schedule(
                    'nl_recruitment.mail_recruitment_panel_member_notification',
                    note=note,
                    user_id=login.id or self.env.user.id)


    @api.onchange("is_published")
    def change_job_status(self):
        for rec in self:
            if rec.job_id and not rec.job_id.is_published and rec.is_published:
                rec.job_id.is_published = True

    @api.model
    def _default_address_id(self):
        return self.env.company.partner_id

    address_id = fields.Many2one(
        'res.partner', "Job Location", default=_default_address_id,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Address where employees are working")


    def _get_default_favorite_user_ids(self):
        return [(6, 0, [self.env.uid])]

    is_favorite = fields.Boolean(compute='_compute_is_favorite', inverse='_inverse_is_favorite')
    favorite_user_ids = fields.Many2many('res.users', 'job_announcement_favorite_user_rel', 'job_announcement_id', 'user_id', default=_get_default_favorite_user_ids)

    def _compute_is_favorite(self):
        for announcement in self:
            announcement.is_favorite = self.env.user in announcement.favorite_user_ids

    def _inverse_is_favorite(self):
        unfavorited_jobs = favorited_jobs = self.env['hr.job.announcement']
        for announcement in self:
            if self.env.user in announcement.favorite_user_ids:
                unfavorited_jobs |= announcement
            else:
                favorited_jobs |= announcement
        favorited_jobs.write({'favorite_user_ids': [(4, self.env.uid)]})
        unfavorited_jobs.write({'favorite_user_ids': [(3, self.env.uid)]})

    def _compute_website_url(self):
        super(JobAnnouncement, self)._compute_website_url()
        for announcement in self:
            announcement.website_url = "/jobs/announcements/detail/%s" % slug(announcement)

    def _compute_document_ids(self):
        applicants = self.mapped('application_ids')
        app_to_job = dict((applicant.id, applicant.job_announcement_id.id) for applicant in applicants)
        attachments = self.env['ir.attachment'].search([('res_model', '=', 'hr.applicant'), ('res_id', 'in', applicants.ids)])
        result = dict.fromkeys(self.ids, self.env['ir.attachment'])
        for attachment in attachments:
            if attachment.res_model == 'hr.applicant':
                result[app_to_job[attachment.res_id]] |= attachment

        for announcement in self:
            announcement.document_ids = result.get(announcement.id, False)
            announcement.documents_count = len(announcement.document_ids)


    def _compute_recruitment_file_ids(self):
        attachments = self.env['ir.attachment'].search([('res_model', '=', 'hr.job.announcement'), ('res_id', 'in', self.ids)])
        result = dict.fromkeys(self.ids, self.env['ir.attachment'])
        for attachment in attachments:
            result[attachment.res_id] |= attachment

        for announcement in self:
            announcement.recruitment_file_ids = result.get(announcement.id, False)
            announcement.recruitment_file_count = len(announcement.recruitment_file_ids)

    def _compute_all_application_count(self):
        read_group_result = self.env['hr.applicant'].with_context(active_test=False).read_group([('job_announcement_id', 'in', self.ids)], ['job_announcement_id'], ['job_announcement_id'])
        result = dict((data['job_announcement_id'][0], data['job_announcement_id_count']) for data in read_group_result)
        for announcement in self:
            announcement.all_application_count = result.get(announcement.id, 0)
    
    def _compute_application_count(self):
        read_group_result = self.env['hr.applicant'].read_group([('job_announcement_id', 'in', self.ids)], ['job_announcement_id'], ['job_announcement_id'])
        result = dict((data['job_announcement_id'][0], data['job_announcement_id_count']) for data in read_group_result)
        for announcement in self:
            announcement.application_count = result.get(announcement.id, 0)

    def _get_first_stage(self):
        self.ensure_one()
        return self.env['hr.recruitment.stage'].search([
            '|',
            ('job_ids', '=', False),
            ('job_ids', '=', self.job_id.id)], order='sequence asc', limit=1)

    def _compute_new_application_count(self):
        for announcement in self:
            announcement.new_application_count = self.env["hr.applicant"].search_count(
                [("job_announcement_id", "=", announcement.id), ("stage_id", "=", announcement._get_first_stage().id)]
            )

    def action_get_attachment_tree_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id("base.action_attachment")
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.ids[0]
        }
        action['search_view_id'] = (self.env.ref('hr_recruitment.ir_attachment_view_search_inherit_hr_recruitment').id, )
        action['domain'] = [('res_model', '=', 'hr.applicant'), ('res_id', 'in', self.mapped('application_ids').ids)]
        return action

    def action_get_applicant_file_attachment_tree_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id("base.action_attachment")
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.ids[0]
        }
        action['search_view_id'] = (self.env.ref('hr_recruitment.ir_attachment_view_search_inherit_hr_recruitment').id, )
        action['domain'] = [('res_model', '=', 'hr.job.announcement'), ('res_id', 'in', self.ids)]
        return action

    def set_recruit(self):
        for record in self:
            record.write({'website_published': True})
            record.change_job_status()
            no_of_recruitment = 1 if record.no_of_recruitment == 0 else record.no_of_recruitment
            record.write({'state': 'recruit', 'no_of_recruitment': no_of_recruitment})
        return True

    def set_open(self):
        self.write({'website_published': False})
        return self.write({
            'state': 'close',
            'no_of_recruitment': 0,
        })

    def reset_as_draft(self):
        self.write({'website_published': False})
        return self.write({
            'state': 'draft'
        })
    
    @api.onchange("is_published")
    def is_publihsed_changed(self):
        for rec in self:
            if rec.is_published and  rec.state != 'recruit':
                raise AccessError(_("You cannot publish an announcement until the recruitment is in-progress stage."))


    @api.model
    def job_expiry(self):
        
        current_date = fields.Date.context_today(self)
        open_jobs = self.search([
            ('state', '=', 'recruit')
        ])
        
        for job in open_jobs:
            if job.vacancy_deadline:
                if job.vacancy_deadline < current_date:
                    job.write({
                        'is_published': False,
                    })
        
        return True

    
    def open_form_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id("nl_recruitment.action_hr_job_announcement_form")
        action['res_id'] = self.id
        return action


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'
    job_announcement_id = fields.Many2one('hr.job.announcement', "Applied Job Position", domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=True)



class EmployeeAnnnouncementLine(models.Model):
    _name = 'employee.announcement.line'

    job_announcement_id = fields.Many2one('hr.job.announcement')
    employee_id = fields.Many2one('hr.employee')
    hire_date = fields.Date()


class EmployeeAnnnouncementLine(models.Model):
    _name = "hr.applicant.score"
    _description = 'Applicant Score'
    _rec_name = 'applicant_id'

    shortlisting_score = fields.Selection(
        [(str(val), str(val)) for val in range(0,11)]
        , required=True)
    score_category = fields.Selection([
        ('poor', 'Poor'),
        ('below_exceptions', 'Below Expectations'),
        ('minor_shortfall', 'Minor Shortfall'),
        ('competent', 'Competent'),
        ('beyond_competent', 'Beyond Competent'),
        ], readonly=True)
    user_id = fields.Many2one('res.users', required=True)
    applicant_id = fields.Many2one('hr.applicant', required=True)
    panel_members = fields.Many2many('res.users')

    @api.onchange('shortlisting_score')
    def compute_score_category(self):
        for rec in self:
            rec.score_category = False
            if rec.shortlisting_score:
                rec.score_category = master_data.SCORE_RANGE_DICT.get(rec.shortlisting_score)

    @api.model
    def default_get(self, fields):
        vals = super(EmployeeAnnnouncementLine, self).default_get(fields)
        context = dict(self._context) or {}
        if context.get("default_applicant_id", False):
            applicant_record = self.env['hr.applicant'].browse(context.get('default_applicant_id'))
            vals['panel_members'] = applicant_record.job_announcement_id.panel_members
        return vals


    @api.constrains('shortlisting_score', 'user_id', 'applicant_id')
    def validate_records(self):
        for rec in self:
            if rec.user_id and rec.applicant_id:
                if rec.user_id.id not in rec.applicant_id.job_announcement_id.panel_members.mapped('id'):
                    raise AccessError(_("Only panel members can score."))
                if self.search_count([('user_id', '=', rec.user_id.id), ('applicant_id', '=', rec.applicant_id.id), ('id', '!=', rec.id)]) > 0:
                    raise AccessError(_("A Panel Member Can Only Score Once Per Applicant."))
                if self.env['hr.applicant.score'].search_count([('applicant_id', '=', rec.applicant_id.id), ('id', '!=', rec.id)]) >= 5:
                    raise AccessError(_("An Applicant Can Be Scored Maximum 5 times."))
            if rec.applicant_id:
                rec.applicant_id.message_post(
                            body=_('Shortlisting Index: %s -> %s') % (rec.user_id.name, rec.shortlisting_score),
                            subtype_xmlid="nl_employee.mt_applicant_reference")


class EmployeeAnnouncementInterviewLine(models.Model):
    _name = "hr.applicant.interview.score"
    _description = 'Applicant Interview Score '
    _rec_name = 'applicant_id'

    # interview_score = fields.Selection(
    #     [(str(val), str(val)) for val in range(0,11)]
    #     , required=True)
    interview_score = fields.Float(required=True)
    user_id = fields.Many2one('res.users', required=True)
    applicant_id = fields.Many2one('hr.applicant')
    panel_members = fields.Many2many('res.users')

    @api.model
    def default_get(self, fields):
        vals = super(EmployeeAnnouncementInterviewLine, self).default_get(fields)
        context = dict(self._context) or {}
        if context.get("default_applicant_id", False):
            applicant_record = self.env['hr.applicant'].browse(context.get('default_applicant_id'))
            vals['panel_members'] = applicant_record.job_announcement_id.panel_members
        return vals

    @api.constrains('interview_score', 'user_id', 'applicant_id')
    def validate_records(self):
        for rec in self:
            if rec.user_id and rec.applicant_id:
                if rec.user_id.id not in rec.applicant_id.job_announcement_id.panel_members.mapped('id'):
                    raise AccessError(_("Only panel members can score."))
                if self.search_count([('user_id', '=', rec.user_id.id), ('applicant_id', '=', rec.applicant_id.id), ('id', '!=', rec.id)]) > 0:
                    raise AccessError(_("A Panel Member Can Only Score Once Per Applicant."))
                if self.env['hr.applicant.score'].search_count([('applicant_id', '=', rec.applicant_id.id), ('id', '!=', rec.id)]) >= 5:
                    raise AccessError(_("An Applicant Can Be Scored Maximum 5 times."))
                if rec.interview_score > 100:
                    raise AccessError(_("An Applicant Can Be Scored in range (1 - 100) only."))
            if rec.applicant_id:
                rec.applicant_id.message_post(
                            body=_('Interview Score: %s -> %s') % (rec.user_id.name, rec.interview_score),
                            subtype_xmlid="nl_employee.mt_applicant_reference")