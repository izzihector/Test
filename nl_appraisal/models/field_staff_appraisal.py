from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime

class EmployeeAppriasal(models.Model):
    _inherit = 'employee.appraisal'

    field_state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('supervisor_review', 'Supervisor Assessment'),
            ('done', 'Done'),
            ('cancel', 'Cancel')
        ],
        default='draft'
        )
    field_prev_state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('supervisor_review', 'Supervisor Assessment'),
            ('done', 'Done'),
            ('cancel', 'Cancel')
        ],
        default='draft',
        readonly=True
        )

    #  Field staff performance assessments part
    field_p1_rating1 = fields.Float(string="Work Performance")
    field_p1_rating2 = fields.Float(string="Discipline")
    field_p1_rating3 = fields.Float(string="Behaviour")
    field_p1_rating4 = fields.Float(string="Puncuality")
    field_p1_rating5 = fields.Float(string="Response to Instructions")
    field_p1_rating6 = fields.Float(string="Helpfulness & Iniiative")
    field_p1_rating7 = fields.Float(string="Respect SCA policies and Values")
    field_p1_rating8 = fields.Float(string="Quality of Work")
    field_p1_rating9 = fields.Float(string="Supervision")
    field_p1_rating10 = fields.Float(string="Efficiency")
    field_p1_total_score = fields.Float(string="Total Performance Assessment Score")

    #  Field staff employee feedback about supervision
    field_p2_q1 = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ])
    field_p2_q1_training_type = fields.Char()
    field_p2_q2 = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ])
    field_p2_q3 = fields.Text()
    field_p2_emp_comments = fields.Text()

    # Over all assessments
    field_overall_assessment = fields.Text()

    # Display tree view state
    display_state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('objective_setting', 'Objective Setting'),
            ('performance_period', 'Performance Period'),
            ('self_review', 'Self Assessment'),
            ('supervisor_review', 'Supervisor Assessment'),
            ('2nd_supervisor_review', '2nd Supervisor Assessment'),
            ('final_comments', 'Final Comments'),
            ('done', 'Done'),
            ('cancel', 'Cancel')
        ],
        compute="_get_display_state", string="Current State", store=True)

    @api.depends('state', 'field_state')
    def _get_display_state(self):
        for rec in self:
            rec.display_state = rec.state if rec.appraisal_type != 'field_staff' else rec.field_state

    def validate_performance_field_staf_assessments(self):
        for rec in self:
            if not rec.field_p1_rating1 or not rec.field_p1_rating2 or not rec.field_p1_rating2 or not rec.field_p1_rating3 or \
                not rec.field_p1_rating4 or not rec.field_p1_rating5 or not rec.field_p1_rating6 or not rec.field_p1_rating7 or not rec.field_p1_rating8 \
                    or not rec.field_p1_rating9 or not rec.field_p1_rating10  :
                raise ValidationError(_("Add all performance assessments ratings."))

    def validate_employee_feedback_field_staff(self):
        for rec in self:
            if not rec.field_p2_q1 or not rec.field_p2_q2 or not rec.field_p2_q3 or not rec.field_p2_emp_comments:
                raise ValidationError(_("Add all employee feedbacks."))
            elif rec.field_p2_q1 and rec.field_p2_q1 == 'yes' and not rec.field_p2_q1_training_type:
                raise ValidationError(_("Add type of training for employee feedback."))

    def validate_sup_field_overall_rating(self):
        for rec in self:
            if not rec.p7_overall_rating and not rec.p7_overall_rating_not_applicable:
                raise ValidationError(_("Please add overall rating for employee."))
    
    def validate_sup_field_overall_assessment(self):
        for rec in self:
            if not rec.field_overall_assessment:
                raise ValidationError(_("Please add overall assessments."))


    @api.constrains('field_state')
    def field_state_validations(self):
        for rec in self:
            if rec.appraisal_type == 'field_staff':
                if rec.field_prev_state == 'supervisor_review':
                    rec.validate_performance_field_staf_assessments()
                    rec.validate_employee_feedback_field_staff()
                    rec.validate_sup_field_overall_rating()
                    rec.validate_sup_field_overall_assessment()

    def move_to_cancel_field(self):
        for rec in self:
            rec.field_prev_state = 'cancel'
            rec.field_state = 'cancel'

    def move_to_field_draft(self):
        for rec in self:
            rec.field_prev_state = 'draft'
            rec.field_state = 'draft'

    def move_to_supervisor_review_field(self):
        """ This function move record to supervisor review """
        context = dict(self._context) or {}
        for rec in self:

            if not rec.employee_id:
                raise ValidationError(_("You Need to Select an Employee First."))

            if context.get('triggred_from_batch_send', False) and rec.state != 'draft':
                continue

            if context.get('delay_appraisals_send_emails', False):
                rec.notify_supervisor_to_field_staff_supervisor_review(force_to_send=False)
            else:
                rec.notify_supervisor_to_field_staff_supervisor_review()


            rec.field_prev_state = rec.field_state
            rec.field_state = 'supervisor_review'
            
            rec.disable_appraisal_type = True

    def move_to_done_stage_field_staff(self):
        """ This function move Done Stage. """
        for rec in self:
            rec.manager_sign_date = rec._get_date_as_utc(datetime.now())
            rec.notify_employee_to_field_staff_self_review()
            rec.field_prev_state = rec.field_state
            rec.field_state = "done"

    # Employee Emails
    def notify_employee_to_field_staff_self_review(self):
        for rec in self:
            reciever_user = rec.employee_id.user_id
            if not reciever_user:
                return False
            
            responsible = rec.get_appraisal_responsible_current_office()
            from_email = responsible and responsible.email or False

            email_template = self.env.ref(
                    'nl_appraisal.appraisal_notify_template')
            body_html = _("""
                    Dear %s <br/><br/>
                    Below is the link for your performance review for the current year. You can access it from the link below or though your portal account.
                    <br/>
                    <br/>
                    <a href="/employee/my-appraisals/%s" class="btn" style="background-color: #875a7b; color: white;">View Appraisal</a>
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
                    'subject': "Appraisal Self Assessment",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=True)

    # Managers emails
    def notify_supervisor_to_field_staff_supervisor_review(self, force_to_send=True):
        for rec in self:
            reciever_user = rec.manager_id.user_id
            if not reciever_user:
                return False

            responsible = rec.get_appraisal_responsible_current_office()
            from_email = responsible and responsible.email or False

            email_template = self.env.ref(
                    'nl_appraisal.appraisal_notify_template')
            body_html = _("""
                    Dear %s <br/><br/>
                    HR has initated the performance appraisal process for all staff. You are kindly requested to use the link below and complete the appraisal for %s. 
                    You can use the link below to access the appraisal record:
                    <br/>
                    <br/>
                    <a href="/supervisor/employee-appraisals/%s" class="btn" style="background-color: #875a7b; color: white;">View Appraisal</a>
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
                    'subject': "Appraisal Supervisor Assessment",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=force_to_send)