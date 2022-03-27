from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz

class PIPAppraisal(models.Model):
    _name = 'appraisal.pip'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
    _rec_name = "employee_id"
    _description = "Performance Improvement Plan"
    
    source_appraisal = fields.Reference(selection=[ 
        ('employee.appraisal', 'Performance Appraisals'),
        ('probation.appraisal', 'Probation Appraisals')],  
        string = "Appraisal For",
        )
    appraisal_type = fields.Selection([
        ('probation_appraisal', 'Probation Appraisal'),
        ('general_appraisal', 'Performance Appraisal')
        ])
    appraisal_model = fields.Char()
    general_apparisal_id = fields.Many2one('employee.appraisal')
    probation_apparisal_id = fields.Many2one('probation.appraisal')


    @api.onchange('source_appraisal')
    def _onchange_source_appraisal(self):
        for rec in self:
            if rec.source_appraisal:
                rec.employee_id = rec.source_appraisal.employee_id
                rec.appraisal_type = 'general_appraisal' if rec.source_appraisal._name == 'employee.appraisal' else 'probation_appraisal'
                rec.appraisal_model = rec.source_appraisal._name
                if rec.source_appraisal._name == 'employee.appraisal':
                    rec.general_apparisal_id = rec.source_appraisal
                else:
                    rec.probation_apparisal_id = rec.source_appraisal

    employee_id = fields.Many2one(
        'hr.employee', 
        string="Employee",
        )
    employee_id_no = fields.Char(
        related='employee_id.idc_no', 
        string="Employee ID",
        readonly=True
        )
    job_id = fields.Many2one(
        comodel_name='hr.job',
        related='employee_id.job_id',
        string="Position Title",
        readonly=True
        )
    unit_id = fields.Many2one(
        comodel_name='hr.unit',
        related='employee_id.unit_id', 
        string="Unit",
        readonly=True
        )
    department_id = fields.Many2one(
        comodel_name='hr.department', 
        related='employee_id.department_id', 
        string="Department", 
        readonly=True
        )
    office_id = fields.Many2one(
        comodel_name='office', 
        related='employee_id.office_id', 
        string='Office',
        readonly=True,
        store=True
        )
    manager_id = fields.Many2one(
        comodel_name='hr.employee', 
        related='employee_id.parent_id',
        string="Line Manager",
        readonly=True,
        store=True
        )
    manager_job_id = fields.Many2one(
        comodel_name='hr.job',
        related='manager_id.job_id',
        string="Line Manager Position",
        readonly=True
        )
    second_manager_id = fields.Many2one(
        comodel_name='hr.employee', 
        related='employee_id.second_manager_id',
        string="2nd Line Manager",
        readonly=True,
        store=True
        )
    second_manager_job_id = fields.Many2one(
        comodel_name='hr.job',
        related='second_manager_id.job_id',
        string="2nd Line Manager Position",
        readonly=True
        )
    other_attendees = fields.Many2many("hr.employee")
    initial_meeting_date = fields.Datetime(string="Date of Initial Metting")
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('planning', 'Planning'),
            ('performance_period', 'Performance Period'),
            ('assessment', 'Assessment'),
            ('final_comments', 'Final Comments'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        ],
        default='draft'
        )
    prev_state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('planning', 'Planning'),
            ('performance_period', 'Performance Period'),
            ('assessment', 'Assessment'),
            ('final_comments', 'Final Comments'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        ],
        default='draft',
        readonly=True
        )
    active = fields.Boolean(default=True)

    target_ids = fields.One2many(
        comodel_name = 'appraisal.pip.target',
        inverse_name = "appraisal_pip_id",
        string="Targets",
        )
    review_ids = fields.One2many(
        comodel_name = 'appraisal.pip.review',
        inverse_name = "appraisal_pip_id",
        string="Reviews",
        )
    
    # Signatture part
    employee_sign_date = fields.Datetime()
    manager_sign_date = fields.Datetime()

    def move_to_draft(self):
        for rec in self:
            rec.prev_state = 'draft'
            rec.state = 'draft'

    def move_to_cancel(self):
        for rec in self:
            rec.prev_state = rec.state
            rec.state = 'cancel'

    def move_to_planning(self):
        for rec in self:
            rec.prev_state = rec.state
            rec.state = 'planning'
            rec.notify_supervisor_to_planning()

    def move_to_performance_period(self):
        for rec in self:
            rec.prev_state = rec.state
            rec.state = 'performance_period'
            rec.notify_employee_to_performance_period()
    
    def move_to_assessment(self):
        for rec in self:
            rec.prev_state = rec.state
            rec.state = 'assessment'
            rec.notify_supervisor_to_assessment()

    def move_to_final_comments(self):
        for rec in self:
            rec.manager_sign_date = self._get_date_as_utc(datetime.now())
            rec.prev_state = rec.state
            rec.state = 'final_comments'
            rec.notify_employee_to_final_comments()

    def move_to_done(self):
        for rec in self:
            rec.employee_sign_date = self._get_date_as_utc(datetime.now())
            rec.prev_state = rec.state
            rec.state = 'done'
            rec.notify_supervisor_to_done()

    @api.constrains('state')
    def state_validations(self):
        for rec in self:
            if rec.prev_state == 'planning':
                rec.validate_targets()
                rec.validate_reviews_date()
            elif rec.prev_state == 'assessment':
                rec.validate_reviews()

    def view_full_pip_form(self):
        return{
            "type": "ir.actions.act_url",
            "url": "/appraisal-pip-view/%s" % (self.id,),
            "target": "new",
        }         

                
    def _get_date_as_utc(self, date):
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        mytz = pytz.timezone(self._context.get('tz') or self.env.user.tz)
        display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(
            str(date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(mytz), "%Y-%m-%d %H:%M:%S")
        return datetime.strptime(display_date_result, "%Y-%m-%d %H:%M:%S")

    def validate_targets(self):
        for rec in self:
            if not rec.target_ids:
                raise ValidationError(_("Please add objectives for the current PIP record under set objectives tab."))
            else: 
                if len(rec.target_ids) >  5:
                    raise ValidationError(_("Maximum 5 PIP objectives can be set."))
                missing_objectives_data = list(filter( lambda x: ( not x.name or not x.performance_concern or not x.agreed_improvement_action or not x.support), rec.target_ids))
                if len(missing_objectives_data) > 0:
                    raise ValidationError(_('You need to fill all 4 fields of an objective for all records under set objectives tab.'))
    
    def validate_reviews_date(self):
        for rec in self:
            if not rec.review_ids:
                raise ValidationError(_("Please add reviews for the current PIP record under set reviews tab."))
            else: 
                if len(rec.review_ids) >  5:
                    raise ValidationError(_("Maximum 5 PIP reviews can be set."))
                missing_objectives_data = list(filter( lambda x: ( not x.review_date), rec.review_ids))
                if len(missing_objectives_data) > 0:
                    raise ValidationError(_('You need to review date for all records under set reviews tab.'))

    def validate_reviews(self):
        for rec in self:
            if not rec.review_ids:
                raise ValidationError(_("Please add reviews for the current PIP record under set reviews tab."))
            else: 
                if len(rec.review_ids) >  5:
                    raise ValidationError(_("Maximum 5 PIP reviews can be set."))
                missing_objectives_data = list(filter( lambda x: (not x.notes or not x.result), rec.review_ids))
                if len(missing_objectives_data) > 0:
                    raise ValidationError(_('You need to fill all fields of review for all records under set reviews tab.'))

    def get_appraisal_responsible_current_office(self):
        for rec in self:
            approver_record = self.env['hr.contract.approver'].sudo().search([('office_id', '=', rec.office_id and rec.office_id.id or False)], limit=1)
            if not approver_record:
                return False
            return approver_record.appraisal_responsible

    # Managers emails
    def notify_supervisor_to_planning(self, force_to_send=True):
        for rec in self:
            reciever_user = rec.manager_id.user_id
            if not reciever_user:
                return False

            responsible = rec.get_appraisal_responsible_current_office()
            from_email = responsible and responsible.email or False

            email_template = self.env.ref(
                    'nl_appraisal.appraisal_pip_notify_template')
            body_html = _("""
                    Dear %s <br/><br/>
                    HR has initiated a Performance Improvement Plan for %s. You are kindly requested to use the link below to access improvement plan record and set targets for the upcoming plan period. 
                    <br/>
                    <br/>
                    <a href="/supervisor/employee-pip-appraisals/%s" class="btn" style="background-color: #875a7b; color: white;">View PIP</a>
                    <br/><br/>
                    Kind regards,
                    <br/>
                    HR Unit, SCA
                """) % (rec.manager_id.name, rec.employee_id.name, rec.id)
            if email_template:
                email_template.sudo().write({
                    'email_from': from_email,
                    'partner_to': reciever_user.partner_id and reciever_user.partner_id.id or '',
                    'email_to': not reciever_user.partner_id and reciever_user.email or '',
                    'subject': "PIP Planning",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=force_to_send)

    def notify_supervisor_to_assessment(self, force_to_send=True):
        for rec in self:
            reciever_user = rec.manager_id.user_id
            if not reciever_user:
                return False

            responsible = rec.get_appraisal_responsible_current_office()
            from_email = responsible and responsible.email or False

            email_template = self.env.ref(
                    'nl_appraisal.appraisal_pip_notify_template')
            body_html = _("""
                    Dear %s <br/><br/>
                    The target date for the Performance Improvement Plan of %s has been met. The HR unit kindly requests that you provide your review note against the targets set using your HRIS portal. Kindly use the link below to access said record.
                    <br/>
                    <br/>
                    <a href="/supervisor/employee-pip-appraisals/%s" class="btn" style="background-color: #875a7b; color: white;">View PIP</a>
                    <br/><br/>
                    Kind regards,
                    <br/>
                    HR Unit, SCA
                """) % (rec.manager_id.name, rec.employee_id.name, rec.id)
            if email_template:
                email_template.sudo().write({
                    'email_from': from_email,
                    'partner_to': reciever_user.partner_id and reciever_user.partner_id.id or '',
                    'email_to': not reciever_user.partner_id and reciever_user.email or '',
                    'subject': "PIP Assessment",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=force_to_send)

    def notify_supervisor_to_done(self, force_to_send=True):
        for rec in self:
            reciever_user = rec.manager_id.user_id
            if not reciever_user:
                return False

            responsible = rec.get_appraisal_responsible_current_office()
            from_email = responsible and responsible.email or False

            email_template = self.env.ref(
                    'nl_appraisal.appraisal_pip_notify_template')
            body_html = _("""
                    Dear %s <br/><br/>
                    Please be informed that Performance Improvement Plan process for %s has been concluded. You can use the link below to access the said record if needed. 
                    <br/>
                    <br/>
                    <a href="/supervisor/employee-pip-appraisals/%s" class="btn" style="background-color: #875a7b; color: white;">View PIP</a>
                    <br/><br/>
                    Kind regards,
                    <br/>
                    HR Unit, SCA
                """) % (rec.manager_id.name, rec.employee_id.name, rec.id)
            if email_template:
                email_template.sudo().write({
                    'email_from': from_email,
                    'partner_to': reciever_user.partner_id and reciever_user.partner_id.id or '',
                    'email_to': not reciever_user.partner_id and reciever_user.email or '',
                    'subject': "PIP Done",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=force_to_send)

    # Employee emails
    def notify_employee_to_performance_period(self, force_to_send=True):
        for rec in self:
            reciever_user = rec.employee_id.user_id
            if not reciever_user:
                return False

            responsible = rec.get_appraisal_responsible_current_office()
            from_email = responsible and responsible.email or False

            email_template = self.env.ref(
                    'nl_appraisal.appraisal_pip_notify_template')
            body_html = _("""
                    Dear %s <br/><br/>
                    Your targets for the duration of your Performance Improvement Plan have been set by your supervisor. You can use the link below to review them or through your portal account. Should you have any issues with them, you can contact your supervisor or HR.
                    <br/>
                    <br/>
                    <a href="/employee/my-pip-appraisals/%s" class="btn" style="background-color: #875a7b; color: white;">View PIP</a>
                    <br/><br/>
                    Kind regards,
                    <br/>
                    HR Unit, SCA
                """) % (rec.employee_id.name, rec.id)
            if email_template:
                email_template.sudo().write({
                    'email_from': from_email,
                    'partner_to': reciever_user.partner_id and reciever_user.partner_id.id or '',
                    'email_to': not reciever_user.partner_id and reciever_user.email or '',
                    'subject': "PIP Performance Period",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=force_to_send)

    def notify_employee_to_final_comments(self, force_to_send=True):
        for rec in self:
            reciever_user = rec.employee_id.user_id
            if not reciever_user:
                return False

            responsible = rec.get_appraisal_responsible_current_office()
            from_email = responsible and responsible.email or False

            email_template = self.env.ref(
                    'nl_appraisal.appraisal_pip_notify_template')
            body_html = _("""
                    Dear %s <br/><br/>
                    Your supervisor has provided their notes against the targets that were set as part of your Performance Improvement Plan. Please use the link below to access your plan record and finalize the process.
                    <br/>
                    <br/>
                    <a href="/employee/my-pip-appraisals/%s" class="btn" style="background-color: #875a7b; color: white;">View PIP</a>
                    <br/><br/>
                    Kind regards,
                    <br/>
                    HR Unit, SCA
                """) % (rec.employee_id.name, rec.id)
            if email_template:
                email_template.sudo().write({
                    'email_from': from_email,
                    'partner_to': reciever_user.partner_id and reciever_user.partner_id.id or '',
                    'email_to': not reciever_user.partner_id and reciever_user.email or '',
                    'subject': "PIP Final Comments",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=force_to_send)

    def auto_move_pip_to_assessment(self):
        """ This function is called via automation and move records to  assessments. """
        records = self.search([('state', '=', 'performance_period')])
        for rec in records:
            unfinalized_reviews = list(filter( lambda x: (not x.finalized), rec.review_ids))
            if len(unfinalized_reviews) > 0:
                unfinalized_date = unfinalized_reviews[0].review_date
            if unfinalized_date and (unfinalized_date - fields.Date.today()).days >= 0:
                rec.sudo().move_to_assessment()

    
    @api.model
    def create(self, vals):
        res = super(PIPAppraisal, self).create(vals)
        employee = res.employee_id
        manager = res.manager_id
        partners = []
        if employee and employee.user_id:
            partners.append(employee.user_id.partner_id.id)
        if manager and manager.user_id:
            partners.append(manager.user_id.partner_id.id)
        if partners: 
            subtype_ids = self.env['mail.message.subtype'].search([('res_model', '=', 'appraisal.pip')]).ids
            res.message_subscribe(
                partner_ids=partners,
                subtype_ids=subtype_ids)
        return res
                
class PIPAppraisalTarget(models.Model):
    _name = 'appraisal.pip.target'
    _rec_name = "name"
    _description = "Performance Improvement Plan Targets"

    appraisal_pip_id = fields.Many2one('appraisal.pip', string="Peformance Improvement Plan")
    name = fields.Text(string="Target Area")
    performance_concern = fields.Text(string="Performance Concern")
    agreed_improvement_action = fields.Text(string="Agreed Imporovement Action")
    support = fields.Text(string="Support")
    
class PIPAppraisalReview(models.Model):
    _name = 'appraisal.pip.review'
    _rec_name = "appraisal_pip_id"
    _description = "Performance Improvement Plan Reviews"

    appraisal_pip_id = fields.Many2one('appraisal.pip', string="Peformance Improvement Plan")
    review_date = fields.Date(string="Review Date")
    archive_date = fields.Datetime(string="Archive Date")
    notes = fields.Text(string="Review Notes")
    result = fields.Selection([
        ('met', 'Met'),
        ('not_met', 'Not Met'),
        ('partially_met', 'Partially Met'),
        ])
    finalized = fields.Boolean(compute="_compute_finalized", store=True)


    @api.depends('review_date', 'notes', 'result')
    def _compute_finalized(self):
        for rec in self:
            rec.finalized = False
            if rec.review_date and rec.notes and rec.result:
                rec.finalized = True 


    