# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz


class EmployeeAppriasalProbation(models.Model):
    _name = 'probation.appraisal'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
    _rec_name = "employee_id"
    _description = "Probation Appraisal"
         

    employee_id = fields.Many2one(
        'hr.employee', 
        string="Employee",
        required=True
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
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('objective_setting', 'Objective Setting'),
            ('probation_period', 'Probation Period'),
            ('self_assessment', 'Self Assessment'),
            ('supervisor_assessment', 'Supervisor Assessment'),
            ('final_comments', 'Final Comments'),
            ('done', 'Done'),
            ('cancel', 'Cancel')
        ],
        default='draft'
        )
    prev_state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('objective_setting', 'Objective Setting'),
            ('probation_period', 'Probation Period'),
            ('self_assessment', 'Self Assessment'),
            ('supervisor_assessment', 'Supervisor Assessment'),
            ('final_comments', 'Final Comments'),
            ('done', 'Done'),
            ('cancel', 'Cancel')
        ],
        default='draft',
        readonly=True
        )
    active = fields.Boolean(
        default=True
        )

    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

    objectives_ids = fields.One2many(
        comodel_name = 'probation.appraisal.objectives',
        inverse_name = "probation_appraisal_id",
        string="Objectives",
    )

    pip_ids = fields.One2many('appraisal.pip', 'probation_apparisal_id', string='pip')    
    pip_id_count = fields.Integer(compute="_get_pip_count")
    
    def _get_pip_count(self):
        for rec in self:
            rec.pip_id_count = len(rec.pip_ids)
    
    def action_open_pips(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("nl_appraisal.appraial_pip_action")
        action['domain'] = [('probation_apparisal_id', '=', self.id)]
        return action
    
    def create_pip(self):
        self.ensure_one()
        tmp_pip = self.env['appraisal.pip'].new({"source_appraisal": self})
        tmp_pip._onchange_source_appraisal()
        values  = tmp_pip._convert_to_write(tmp_pip._cache)
        self.env['appraisal.pip'].create(values)
    
    @api.model
    def create(self, vals):
        res = super(EmployeeAppriasalProbation, self).create(vals)
        employee = res.employee_id
        manager = res.manager_id
        partners = []
        if employee and employee.user_id:
            partners.append(employee.user_id.partner_id.id)
        if manager and manager.user_id:
            partners.append(manager.user_id.partner_id.id)
        if partners: 
            subtype_ids = self.env['mail.message.subtype'].search([('res_model', '=', 'probation.appraisal')]).ids
            res.message_subscribe(
                partner_ids=partners,
                subtype_ids=subtype_ids)
        return res

    # This two fields should be filled in self assessment state
    emp_major_achievements = fields.Text()
    p3_emp_comments = fields.Text()

    P2_STATES = [
        ('improvement_required', 'Improvement Required'),
        ('average', 'Average'),
        ('good', 'Good'),
        ('excellent', 'Excellent')
    ]

    p2_q1 = fields.Selection(P2_STATES)
    p2_q2 = fields.Selection(P2_STATES)
    p2_q3 = fields.Selection(P2_STATES)
    p2_q4 = fields.Selection(P2_STATES)
    p2_q5 = fields.Selection(P2_STATES)

    p3_q1 = fields.Text()
    p3_q2 = fields.Text()
    p3_q3 = fields.Text()
    p3_sup_comments = fields.Text()

    p4_q1 = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ])

    p4_q2 = fields.Selection([
        ('termination', 'Termination of Contract'),
        ('improvement', 'Performance Improvement Plan')
    ])

    employee_sign_date = fields.Datetime()
    manager_sign_date = fields.Datetime()

    def move_to_draft(self):
        self.ensure_one()
        self.write({
            'state': 'draft'
        })

    def move_to_cancel(self):
        self.ensure_one()
        self.write({
            'state': 'cancel'
        })

    def start_probation(self):
        self.ensure_one()
        self.write({
            'state': 'objective_setting'
        })
        self.action_send_objective_setting_mail()

    def move_to_probation_period(self):
        self.ensure_one()
        self.validate_general_objectives()
        self.write({
            'state': 'probation_period'
        })
        self.action_send_probation_period_mail()

    def move_to_self_assessment(self):
        self.ensure_one()
        self.validate_general_objectives()
        self.write({
            'state': 'self_assessment'
        })
        self.action_send_self_assessment_email()

    def move_to_supervisor_assessment(self):
        self.ensure_one()
        self.write({
            'state': 'supervisor_assessment'
        })
        self.action_send_supervisor_assessment_mail()

    def move_to_final_commnets(self):
        self.ensure_one()
        self.validate_assessments()
        self.validate_performance()
        self.validate_way_forward()
        self.write({
            'state': 'final_comments',
            'manager_sign_date': self._get_date_as_utc(datetime.now())
        })
        self.action_send_final_comments_mail()

    def move_to_done_stage(self):
        self.ensure_one()
        self.write({
            'state': 'done',
            'employee_sign_date': self._get_date_as_utc(datetime.now())
        })
        self.action_send_done_mail()

    def validate_general_objectives(self):
        for rec in self:
            if not rec.objectives_ids:
                raise ValidationError(_("Please add general objectives for employee under general objectives tab."))
            else: 
                if len(rec.objectives_ids) >  3:
                    raise ValidationError(_("Maximum 3 general objectives can be set."))
                missing_objectives_data = list(filter( lambda x: ( not x.name or not x.expected_outcome), rec.objectives_ids))
                if len(missing_objectives_data) > 0:
                    raise ValidationError(_('You need to fill both objective and expected outcome fields for all records under general objectives tab.'))

    def validate_self_assessments(self):
        for rec in self:
            if not rec.p3_emp_comments or not rec.emp_major_achievements:
                raise ValidationError('Please fill all inputs of Employee Assessments Tab.')

    def validate_assessments(self):
        for rec in self:
            if not all([rec.p2_q1, rec.p2_q2, rec.p2_q3, rec.p2_q4, rec.p2_q5]):
                raise ValidationError(_('Please fill all inputs of Assessment Tab'))

    def validate_performance(self):
        for rec in self:
            if not all([rec.p3_q1, rec.p3_q2, rec.p3_q3, rec.p3_sup_comments]):
                raise ValidationError(_('Please fill all inputs of Performance Tab'))

    def validate_way_forward(self):
        for rec in self:
            if not rec.p4_q1 or (rec.p4_q1 == 'no' and not rec.p4_q2):
                raise ValidationError('Please fill all inputs of Way Forward Tab')


    def _get_date_as_utc(self, date):
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        mytz = pytz.timezone(self._context.get('tz') or self.env.user.tz)
        display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(
            str(date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(mytz), "%Y-%m-%d %H:%M:%S")
        return datetime.strptime(display_date_result, "%Y-%m-%d %H:%M:%S")
   
    def action_send_objective_setting_mail(self):
        for rec in self:
            reciever_user = rec.manager_id.user_id
            if not reciever_user:
                return False

            responsible = rec.get_appraisal_responsible_current_office()
            from_email = responsible and responsible.email or False

            email_template = self.env.ref(
                    'nl_appraisal.probation_appraisal_notify_template')
            body_html = _("""
                    <p>Dear %s,</p>
                    <br/>
                    <p>HR has initiated the probation appraisal for %s. You are kindly requested to use the link below to access their probation appraisal record and set their objective for the upcoming probationary period. </p>
                    <br/>
                    <a target="_blank" href="/supervisor/employee-probation-appraisals/%s" class="btn" style="background-color: #875a7b; color: white;">View Appraisal</a>
                    <br/>
                    <br/>
                    <p>Kind Regards,</p>
                    <p>HR Unit, SCA</p>
                """) % (rec.manager_id.name, rec.employee_id.name, rec.id)
            if email_template:
                email_template.sudo().write({
                    'email_from': from_email,
                    'partner_to': reciever_user.partner_id and reciever_user.partner_id.id or '',
                    'email_to': not reciever_user.partner_id and reciever_user.email or '',
                    'subject': "Porbation Appraisal Objectives Setting",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=True)

    def action_send_probation_period_mail(self):
        for rec in self:
            reciever_user = rec.employee_id.user_id
            if not reciever_user:
                return False

            responsible = rec.get_appraisal_responsible_current_office()
            from_email = responsible and responsible.email or False

            email_template = self.env.ref(
                    'nl_appraisal.probation_appraisal_notify_template')
            body_html = _("""
                   <p>Dear %s,</p>
                    <br/>
                    <p>Your objectives for the current probationary period have been set as part of your probation appraisal record. You can use the link below to review them. Should you have any issues with them, you can contact your supervisor or HR.</p>
                    <br/>
                    <a target="_blank" href="/employee/my-probation-appraisals/%s" class="btn" style="background-color: #875a7b; color: white;">View Appraisal</a>
                    <br/>
                    <br/>
                    <p>Kind Regards,</p>
                    <p>HR Unit, SCA</p>
                """) % (rec.employee_id.name, rec.id)
            if email_template:
                email_template.sudo().write({
                    'email_from': from_email,
                    'partner_to': reciever_user.partner_id and reciever_user.partner_id.id or '',
                    'email_to': not reciever_user.partner_id and reciever_user.email or '',
                    'subject': "Porbation Appraisal Objectives",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=True)

    def action_send_self_assessment_email(self):
        for rec in self:
            reciever_user = rec.employee_id.user_id
            if not reciever_user:
                return False

            responsible = rec.get_appraisal_responsible_current_office()
            from_email = responsible and responsible.email or False

            email_template = self.env.ref(
                    'nl_appraisal.probation_appraisal_notify_template')
            body_html = _("""
                   <p>Dear %s,</p>
                    <br/>
                    <p>Your probation appraisal is now in self assessment stage, You can use the link below to view and submit your comments. Should you have any issues with them, you can contact your supervisor or HR.</p>
                    <br/>
                    <a target="_blank" href="/employee/my-probation-appraisals/%s" class="btn" style="background-color: #875a7b; color: white;">View Appraisal</a>
                    <br/>
                    <br/>
                    <p>Kind Regards,</p>
                    <p>HR Unit, SCA</p>
                """) % (rec.employee_id.name, rec.id)
            if email_template:
                email_template.sudo().write({
                    'email_from': from_email,
                    'partner_to': reciever_user.partner_id and reciever_user.partner_id.id or '',
                    'email_to': not reciever_user.partner_id and reciever_user.email or '',
                    'subject': "Porbation Appraisal Self Assessment",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=True)

    def action_send_supervisor_assessment_mail(self):
        for rec in self:
            reciever_user = rec.manager_id.user_id
            if not reciever_user:
                return False

            responsible = rec.get_appraisal_responsible_current_office()
            from_email = responsible and responsible.email or False

            email_template = self.env.ref(
                    'nl_appraisal.probation_appraisal_notify_template')
            body_html = _("""
                    <p>Dear %s,</p>
                    <br/>
                    <p>The probation period for %s, has almost ended. The HR unit kindly requests that you complete their probation appraisal form using your HRIS portal using the ‘Suboordinate Probation Appraisals’ menu. Kindly use the link below to access said record.</p>
                    <br/>
                    <a target="_blank" href="/supervisor/employee-probation-appraisals/%s" class="btn" style="background-color: #875a7b; color: white;">View Appraisal</a>
                    <br/>
                    <br/>
                    <p>Kind Regards,</p>
                    <p>HR Unit, SCA</p>
                """) % (rec.manager_id.name, rec.employee_id.name, rec.id)
            if email_template:
                email_template.sudo().write({
                    'email_from': from_email,
                    'partner_to': reciever_user.partner_id and reciever_user.partner_id.id or '',
                    'email_to': not reciever_user.partner_id and reciever_user.email or '',
                    'subject': "Porbation Appraisal Supervisor Assessment",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=True)

    def action_send_final_comments_mail(self):
        for rec in self:
            reciever_user = rec.employee_id.user_id
            if not reciever_user:
                return False

            responsible = rec.get_appraisal_responsible_current_office()
            from_email = responsible and responsible.email or False

            email_template = self.env.ref(
                    'nl_appraisal.probation_appraisal_notify_template')
            body_html = _("""
                   <p>Dear %s,</p>
                    <br/>
                    <p>Your supervisor has completed their assessment of your performance during your probationary period. Please use the link below to to access your probation appraisal record and finalize the process. </p>
                    <br/>
                    <a target="_blank" href="/employee/my-probation-appraisals/%s" class="btn" style="background-color: #875a7b; color: white;">View Appraisal</a>
                    <br/>
                    <br/>
                    <p>Kind Regards,</p>
                    <p>HR Unit, SCA</p>
                """) % (rec.employee_id.name, rec.id)
            if email_template:
                email_template.sudo().write({
                    'email_from': from_email,
                    'partner_to': reciever_user.partner_id and reciever_user.partner_id.id or '',
                    'email_to': not reciever_user.partner_id and reciever_user.email or '',
                    'subject': "Porbation Appraisal Final Comments",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=True)

    def action_send_done_mail(self):
        for rec in self:
            reciever_user = rec.manager_id.user_id
            if not reciever_user:
                return False

            responsible = rec.get_appraisal_responsible_current_office()
            from_email = responsible and responsible.email or False

            email_template = self.env.ref(
                    'nl_appraisal.probation_appraisal_notify_template')
            body_html = _("""
                    <p>Dear %s,</p>
                    <br/>
                    <p>Please be informed that probation appraisal process for %s is now complete. You can use the link below to access the said record if needed.</p>
                    <br/>
                    <a target="_blank" href="/supervisor/employee-probation-appraisals/%s" class="btn" style="background-color: #875a7b; color: white;">View Appraisal</a>
                    <br/>
                    <br/>
                    <p>Kind Regards,</p>
                    <p>HR Unit, SCA</p>
                """) % (rec.manager_id.name, rec.employee_id.name, rec.id)
            if email_template:
                email_template.sudo().write({
                    'email_from': from_email,
                    'partner_to': reciever_user.partner_id and reciever_user.partner_id.id or '',
                    'email_to': not reciever_user.partner_id and reciever_user.email or '',
                    'subject': "Porbation Appraisal Done",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=True)

    def get_appraisal_responsible_current_office(self):
        for rec in self:
            approver_record = self.env['hr.contract.approver'].sudo().search([('office_id', '=', rec.office_id and rec.office_id.id or False)], limit=1)
            if not approver_record or not approver_record.appraisal_responsible:
                return False
            return approver_record.appraisal_responsible

    def auto_move_probation_appraisal_to_supervisor_assessment(self):
        """ This function is called via automation and move records to supervisor assessment. """
        records = self.search([('state', '=', 'probation_period')])
        for rec in records:
            if rec.end_date and (rec.end_date - date.today()).days < 8:
                rec.move_to_self_assessment()

    def view_appraisal(self):
        self.ensure_one()
        return{
            "type": "ir.actions.act_url",
            "url": "/probation-appraisal-view/%s" % (self.id,),
            "target": "new",
        }

