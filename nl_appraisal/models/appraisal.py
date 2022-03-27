# -*- coding: utf-8 -*-

from email.policy import default
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz

class EmployeeAppriasal(models.Model):
    _name = 'employee.appraisal'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
    _rec_name = "employee_id"
    _description = "Employee Appraisal"
         

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
    second_manager_id = fields.Many2one(
        comodel_name='hr.employee', 
        related='manager_id.parent_id',
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
    state = fields.Selection(
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
        default='draft'
        )
    prev_state = fields.Selection(
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
        default='draft',
        readonly=True
        )
    active = fields.Boolean(default=True)

    @api.model
    def default_get(self, d_fields):
        vals = super(EmployeeAppriasal, self).default_get(d_fields)
        current_year_start = fields.Date.today().replace(day=1, month=3)
        current_year_end = fields.Date.today().replace(current_year_start.year+1, day=28, month=2)
        vals['review_period_start_date'] = current_year_start
        vals['review_period_end_date'] = current_year_end
        return vals

    
    review_period_start_date = fields.Date(tracking=True)
    review_period_end_date = fields.Date(tracking=True)
    meeting_id = fields.Many2one('calendar.event', string='Meeting')
    date_final_interview = fields.Date(string="Final Interview", index=True, tracking=True)
    token = fields.Char()

    # Part 3 Fields
    p3_q1_emp_comments = fields.Text()
    p3_q1_sup_comments = fields.Text()
    p3_q2_emp_comments = fields.Text()
    p3_q2_sup_comments = fields.Text()
    p3_q3_emp_comments = fields.Text()
    p3_q3_sup_comments = fields.Text()
    p3_q4_emp_comments = fields.Text()
    p3_q4_sup_comments = fields.Text()

    # Part 4 fields
    p4_emp_feed1 = fields.Text()
    p4_emp_feed2 = fields.Text()
    p4_emp_feed3 = fields.Text()
    p4_emp_feed4 = fields.Text()
    p4_emp_comments = fields.Text()
    p4_sup_comments = fields.Text()

    # part 5 and 2ndline
    objectives_ids = fields.One2many(
        comodel_name = 'employee.appraisal.objectives',
        inverse_name = "appraisal_id",
        string="Objectives",
        )
    individual_objectives_ids = fields.One2many(
        comodel_name = 'employee.appraisal.objectives',
        inverse_name = "individual_appraisal_id",
        string="Objectives"
        )
    next_review_objectives_ids = fields.One2many(
        comodel_name = 'employee.appraisal.objectives',
        inverse_name = "next_appraisal_id",
        string="Objectives"
        )
    next_individual_obj1 = fields.Text()
    next_individual_obj2 = fields.Text()
    # part 6 fields
    p6_emp_feed1 = fields.Text()

    # part 7 fields
    p7_overall_rating = fields.Float(tracking=True)
    p7_overall_result = fields.Char(compute="_get_p7_final_result", store=True, tracking=True)
    p7_overall_rating_not_applicable = fields.Boolean()
    p7_emp_contract_rec = fields.Selection([
        ('extension_of_contract', 'Extension of contract'),
        ('non_renewal_of_contract', 'Non-renewal of contract'),
        ('termination_of_contract', 'Termination of contract'), 
        ('performance_improvement_plan', 'Performance Improvement plan (Consult HR for process)'), 
        ], tracking=True)

    # part 8 fields
    p8_2sup_q1 = fields.Selection([
        ("yes", 'Yes'),
        ("no", 'No')
        ])
    p8_2sup_q1_reason = fields.Text()
    p8_2sup_q2 = fields.Selection([
        ("yes", 'Yes directly'),
        ("no", 'No, only through the direct line manager'),
        ("other", 'Technical manager/ Line Director'),
        ])
    
    # part 9 fields
    p9_emp_feed = fields.Selection([
        ("yes", "I Agree"),
        ("no", "I Do Not Agree"),
        ])
    p9_emp_feed_comments = fields.Text()

    # Signatture part
    employee_sign_date = fields.Datetime()
    manager_sign_date = fields.Datetime()
    second_manager_sign_date = fields.Datetime()
    
    # Discussion model
    discussion_ids = fields.One2many(
        comodel_name = 'employee.appraisal.discussion',
        inverse_name = "appraisal_id",
    )
    discussion_ids_count = fields.Integer(compute="_get_disussion_count")
    def view_full_appraisal_form(self):
        return{
            "type": "ir.actions.act_url",
            "url": "/appraisal-view/%s" % (self.id,),
            "target": "new",
        }
    
    # Other fields
    appraisal_type = fields.Selection([
        ('admin_staff', 'Annual Performance Review'),
        ('field_staff', 'Entry Level/Support Staff'),
        ], required=True)
    pip_ids = fields.One2many('appraisal.pip', 'general_apparisal_id', string='pip')    
    pip_id_count = fields.Integer(compute="_get_pip_count")
    
    def _get_pip_count(self):
        for rec in self:
            rec.pip_id_count = len(rec.pip_ids)
    
    disable_appraisal_type = fields.Boolean(default=False)

    @api.depends('p7_overall_rating')
    def _get_p7_final_result(self):
        for rec in self:
            if rec.p7_overall_rating_not_applicable:
                rec.p7_overall_result = 'N/A'
            else:
                if  1 <= rec.p7_overall_rating <= 1.4:
                    rec.p7_overall_result = 'Unsatisfactory/Unacceptable performance'
                elif 1.5 <= rec.p7_overall_rating <= 2.4:
                    rec.p7_overall_result = 'Required performance improvement'
                elif 2.5 <= rec.p7_overall_rating <= 3.4:
                    rec.p7_overall_result = 'Meets Expected Performance'
                elif 3.5 <= rec.p7_overall_rating <= 4.4:
                    rec.p7_overall_result = 'Exceeds Expected Performance'
                elif 4.5 <= rec.p7_overall_rating <= 5:
                    rec.p7_overall_result = 'Exceptional/outstanding'


    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for rec in self:
            if rec.employee_id:
                if rec.employee_id.appraisal_type and rec.employee_id.appraisal_type != 'none':
                    rec.appraisal_type = rec.employee_id.appraisal_type
                else:
                    rec.appraisal_type = 'admin_staff'

    def create_pip(self):
        self.ensure_one()
        tmp_pip = self.env['appraisal.pip'].new({"source_appraisal": self})
        tmp_pip._onchange_source_appraisal()
        values  = tmp_pip._convert_to_write(tmp_pip._cache)
        self.env['appraisal.pip'].create(values)

    def _get_disussion_count(self):
        for rec in self:
            rec.discussion_ids_count = len(rec.discussion_ids)

    def validate_general_objectives(self):
        for rec in self:
            if not rec.objectives_ids:
                raise ValidationError(_("Please add general objectives for employee under general objectives tab."))
            else: 
                if len(rec.objectives_ids) >  5:
                    raise ValidationError(_("Maximum 5 general objectives can be set."))
                missing_objectives_data = list(filter( lambda x: ( not x.name or not x.expected_outcome), rec.objectives_ids))
                if len(missing_objectives_data) > 0:
                    raise ValidationError(_('You need to fill both objective and expected outcome fields for all records under general objectives tab.'))

    def validate_learning_objectives(self):
        for rec in self:
            if not rec.individual_objectives_ids:
                raise ValidationError(_("Please add learning objectives for employee under learning objectives tab."))
            if rec.individual_objectives_ids and len(rec.individual_objectives_ids) > 2:
                raise ValidationError(_("Maximum 2 learning objectives can be set."))

    def validate_general_objectives_sup_feedback(self):
        for rec in self:
            missing_objectives = list(filter( lambda x: ( not x.manager_feedback or not x.rating), rec.objectives_ids))
            if len(missing_objectives) > 0:
                raise ValidationError(_('You need to add feedback and rating to all general objectives.'))

    def validate_learning_objectives_sup_feedback(self):
        for rec in self:
            individual_objectives_ids = list(filter( lambda x: ( not x.manager_feedback), rec.individual_objectives_ids))
            if len(individual_objectives_ids) > 0:
                raise ValidationError(_('You need to add feedback and rating to all learning objectives.'))

    def validate_employee_sup_assessments(self):
        for rec in self:
            if not rec.p3_q1_sup_comments or not rec.p3_q2_sup_comments or not rec.p3_q3_sup_comments or not \
                    rec.p3_q4_sup_comments:
                    raise ValidationError(_("Add all employee assessments feedbacks."))

    def validate_employee_sup_career(self):
        for rec in self:
            if not rec.p4_sup_comments:
                raise ValidationError(_("Add all employee career aspiration feedbacks for an employee."))

    def validate_general_objectives_next(self):
        for rec in self:
            if not rec.next_review_objectives_ids:
                raise ValidationError(_("Please add general objectives for next year under set next year general objectives tab."))
            else: 
                if len(rec.next_review_objectives_ids) >  5:
                    raise ValidationError(_("Maximum 5 general objectives can be set for next year."))
                missing_objectives_data = list(filter( lambda x: ( not x.name or not x.expected_outcome), rec.next_review_objectives_ids))
                if len(missing_objectives_data) > 0:
                    raise ValidationError(_('You need to fill both objective and expected outcome fields for all records under set next year general objectives tab.'))

    def validate_next_year_learning_obj(self):
        for rec in self:
            if not rec.next_individual_obj1 or not rec.next_individual_obj2:
                raise ValidationError(_("Add Learning Objectives for next year."))
    
    def validate_sup_performance_rating(self):
        for rec in self:
            if not rec.p7_emp_contract_rec or (not rec.p7_overall_rating and not rec.p7_overall_rating_not_applicable):
                raise ValidationError(_("Please add performance rating for employee."))
    
    def validate_2nd_sup_fields(self):
        for rec in self:
            if (not rec.p8_2sup_q1 or not rec.p8_2sup_q1_reason or not rec.p8_2sup_q2):
                raise ValidationError(_("Add answeres for appraisal for the second manger review. "))  

    def validate_general_objectives_emp_feedback(self):
        for rec in self:
            if len(list(filter( lambda x: ( not x.employee_feedback), rec.objectives_ids))) > 0:
                raise ValidationError(_('You need to add feedback to all general objectives.'))

    def validate_leaning_objectives_emp_feedback(self):
        for rec in self:
            if len(list(filter( lambda x: ( not x.employee_feedback), rec.individual_objectives_ids))) > 0:
                raise ValidationError(_('You need to add feedback to all learning objectives.'))
    
    def validate_employee_emp_assessments(self):
        for rec in self:
            if not rec.p3_q1_emp_comments or not rec.p3_q2_emp_comments or not rec.p3_q3_emp_comments or not rec.p3_q4_emp_comments:
                raise ValidationError(_("Add all employee assessments feedbacks."))
    
    def validate_employee_emp_career(self):
        for rec in self:
            if not rec.p4_emp_feed1 or not rec.p4_emp_feed2 or not rec.p4_emp_feed3 or not rec.p4_emp_feed4 or not rec.p4_emp_comments:
                raise ValidationError(_("Add all employee career aspiration feedbacks."))        
    
    def validate_employee_upward_feedback(self):
        for rec in self:
            if not rec.p6_emp_feed1:
                raise ValidationError(_("Add upward employee feedbacks."))

    def validate_emp_final_comments(self):
        for rec in self:
            if not rec.p9_emp_feed or not rec.p9_emp_feed_comments:
                raise ValidationError(_("Add your comments."))
 
    @api.constrains('state')
    def state_validations(self):
        for rec in self:
            if rec.prev_state == 'objective_setting':
                rec.validate_general_objectives()
                rec.validate_learning_objectives()
            elif rec.prev_state == 'supervisor_review':
                rec.validate_employee_sup_assessments()
                rec.validate_employee_sup_career()
                rec.validate_general_objectives_sup_feedback()
                rec.validate_learning_objectives_sup_feedback()
                rec.validate_general_objectives_next()
                rec.validate_next_year_learning_obj()
                rec.validate_sup_performance_rating()
            elif rec.prev_state == "2nd_supervisor_review":
                rec.validate_2nd_sup_fields()
            elif rec.prev_state == 'self_review': 
                rec.validate_general_objectives_emp_feedback()
                rec.validate_leaning_objectives_emp_feedback()
                rec.validate_employee_emp_assessments()
                rec.validate_employee_emp_career()
                rec.validate_employee_upward_feedback()
            elif rec.prev_state == "final_comments":
                rec.validate_emp_final_comments() 
            
            
    def _get_date_as_utc(self, date):
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        mytz = pytz.timezone(self._context.get('tz') or self.env.user.tz)
        display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(
            str(date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(mytz), "%Y-%m-%d %H:%M:%S")
        return datetime.strptime(display_date_result, "%Y-%m-%d %H:%M:%S")

    def calculate_performance_rating(self):
        for rec in self:
            rec.p7_overall_rating = sum(list(map(lambda obj : int(obj.rating), rec.objectives_ids))) / len(rec.objectives_ids)

    def move_to_cancel(self):
        for rec in self:
            rec.prev_state = 'cancel'
            rec.state = 'cancel'

    def move_to_draft(self):
        for rec in self:
            rec.prev_state = 'draft'
            rec.state = 'draft'


    def move_to_batch_objective_settings(self):
        """ This function move record to objective setting state. """
        context = dict(self._context) or {}
        for rec in self:
            if rec.appraisal_type == 'field_staff' or rec.state != 'draft':
                continue

            if context.get('delay_appraisals_send_emails', False):
                rec.notify_supervisor_to_objective_setting(force_to_send=False)
            else:
                rec.notify_supervisor_to_objective_setting()

            rec.prev_state = rec.state
            rec.state = 'objective_setting'
    
    def move_to_batch_self_review(self):
        """ This function move record to self assessments state. """
        context = dict(self._context) or {}
        for rec in self:
            if (context.get('triggred_from_batch_send', False) and rec.state != 'performance_period') or rec.appraisal_type == 'field_staff':
                continue
            rec.notify_employee_to_self_review()
            rec.prev_state = rec.state
            rec.state = 'self_review'


    def move_to_objective_settings(self):
        """ This function move record to objective setting state. """
        context = dict(self._context) or {}
        for rec in self:
            if not rec.employee_id:
                raise ValidationError(_("You Need to Select an Employee First."))

            if context.get('delay_appraisals_send_emails', False):
                rec.notify_supervisor_to_objective_setting(force_to_send=False)
            else:
                rec.notify_supervisor_to_objective_setting()


            rec.prev_state = rec.state
            rec.state = 'objective_setting'

            rec.disable_appraisal_type = True

    @api.model
    def create(self, vals):
        res = super(EmployeeAppriasal, self).create(vals)
        employee = res.employee_id
        manager = res.manager_id
        partners = []
        if employee and employee.user_id:
            partners.append(employee.user_id.partner_id.id)
        if manager and manager.user_id:
            partners.append(manager.user_id.partner_id.id)
        if partners: 
            subtype_ids = self.env['mail.message.subtype'].search([('res_model', '=', 'employee.appraisal')]).ids
            res.message_subscribe(
                partner_ids=partners,
                subtype_ids=subtype_ids)
        return res

    def move_to_performance_period(self):
        """ This function move record to performace period state. """
        for rec in self:
            rec.notify_employee_to_performance_period()
            rec.prev_state = rec.state
            rec.state = 'performance_period'

    def move_to_self_review(self):
        """ This function move record to self assessments state. """
        context = dict(self._context) or {}
        for rec in self:
            if context.get('triggred_from_batch_send', False) and rec.state != 'performance_period':
                continue
            rec.notify_employee_to_self_review()
            rec.prev_state = rec.state
            rec.state = 'self_review'

    def move_to_sup_review(self):
        """ This function move record to self supervisor state. """
        for rec in self:
            rec.notify_supervisor_to_supervisor_review()
            rec.prev_state = rec.state
            rec.state = 'supervisor_review'

    def move_to_2ndsup_review(self):
        """ This function move record to 2nd Supervisor Assessment stage. """
        for rec in self:
            rec.notify_second_supervisor_to_2nd_review_stage()
            rec.manager_sign_date = self._get_date_as_utc(datetime.now())
            rec.prev_state = rec.state
            rec.state = "2nd_supervisor_review"

    def move_to_final_comments(self):
        """ This function move record to final comments stage. """
        for rec in self:
            rec.notify_employee_to_final_comments()
            rec.prev_state = rec.state
            if rec.prev_state == 'supervisor_review':
                rec.manager_sign_date = self._get_date_as_utc(datetime.now())
            else:
                rec.second_manager_sign_date = self._get_date_as_utc(datetime.now())
            rec.state = "final_comments"
    
    def move_to_done_stage(self):
        """ This function move Done Stage. And create new record for the current employee for next year. """
        for rec in self:
            next_appraisal_start = rec.review_period_end_date.replace(day=1, month=3)
            next_appraisal_end = rec.review_period_end_date.replace(next_appraisal_start.year+1, day=28, month=2)
            next_year_appraisal = self.env['employee.appraisal'].create({
                "employee_id": rec.employee_id.id,
                "review_period_start_date": next_appraisal_start,
                "review_period_end_date": next_appraisal_end,
                'appraisal_type': 'admin_staff'
            })
            next_year_appraisal.move_to_performance_period()
            # Create general objectives
            for next_object in rec.next_review_objectives_ids:
                self.env['employee.appraisal.objectives'].create({
                    "name": next_object.name,
                    "expected_outcome": next_object.expected_outcome,
                    "appraisal_id": next_year_appraisal.id,
                    })
            # # Create Learning Objectives
            self.env['employee.appraisal.objectives'].create({
                "name": rec.next_individual_obj1,
                "individual_appraisal_id": next_year_appraisal.id,
                })
            self.env['employee.appraisal.objectives'].create({
                "name": rec.next_individual_obj2,
                "individual_appraisal_id": next_year_appraisal.id,
                })

            rec.employee_sign_date = self._get_date_as_utc(datetime.now())
            rec.prev_state = rec.state
            rec.state = "done"
        
    @api.constrains('review_period_start_date', 'review_period_end_date')
    def validate_appraisal_date(self):
        for rec in self:
            if rec.review_period_start_date and rec.review_period_end_date and rec.review_period_start_date >= rec.review_period_end_date:
                raise ValidationError(_("Appraisal Review start date should be less than end date."))
    

    def action_calendar_event(self):
        self.ensure_one()
        partners = self.employee_id.user_id.partner_id | self.env.user.partner_id
        action = self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
        action['context'] = {
            'default_partner_ids': partners.ids,
            'search_default_mymeetings': 1
        }
        return action

    def action_open_discussion(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("nl_appraisal.action_open_appraisal_discussion")
        action['domain'] = [('appraisal_id', '=', self.id)]
        action['context'] = {'default_appraisal_id': self.id}
        return action

    def action_open_pips(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("nl_appraisal.appraial_pip_action")
        action['domain'] = [('general_apparisal_id', '=', self.id)]
        return action

    def auto_move_appraisal_to_self_review(self):
        """ This function is called via automation and move records to self assessments. """
        records = self.search([('state', '=', 'performance_period')])
        for rec in records:
            if rec.review_period_end_date and (rec.review_period_end_date - date.today()).days < 31:
                rec.move_to_self_review()
    
    def get_appraisal_responsible_current_office(self):
        for rec in self:
            approver_record = self.env['hr.contract.approver'].sudo().search([('office_id', '=', rec.office_id and rec.office_id.id or False)], limit=1)
            if not approver_record:
                return False
            return approver_record.appraisal_responsible

    # Employee Emails
    def notify_employee_to_self_review(self):
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
                    With the current performance appraisal period at its end, the HR unit kindly requests that you complete the self-assessment section of your 
                    appraisal record using your HRIS portal. Kindly use the link below to access your appraisal record.
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

    def notify_employee_to_performance_period(self):
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
                    Your objectives for the current year have been set as part of your performance appraisal record. You can use the link below to review them.
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
                    'subject': "Appraisal Performance Period",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=True)
    
    def notify_employee_to_final_comments(self):
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
                    Please be informed that your performance appraisal for the current year is complete. 
                    Please refer to the link below to access and review and finalize your appraisal record for the year, as well as review the objectives set for the upcoming year
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
                    'subject': "Appraisal Final Comments",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=True)
    
    def notify_objectives_changes(self):
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
                    Your supervisor has made some changes to your objectives for the current appraisal period. Kindly visit your portal to review them
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
                    'subject': "Appraisal Objectives Changes",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=True)

    # Managers emails
    def notify_supervisor_to_objective_setting(self, force_to_send=True):
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
                    HR has initiated the performance appraisal for %s for the current year. You are kindly requested to use the link below to draft and finalize their objectives accordingly.
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
                    'subject': "Appraisal Objective Setting",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=force_to_send)

    def notify_supervisor_to_supervisor_review(self):
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
                    %s has completed their self-assessment as part of their performance appraisal for the current year. You are kindly requested to use the link below and complete the appraisal sections related to you.
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
                email_template.send_mail(rec.id, force_send=True)

    def notify_second_supervisor_to_2nd_review_stage(self):
        for rec in self:
            reciever_user = rec.second_manager_id and rec.second_manager_id.user_id or False
            if not reciever_user:
                return False
                
            responsible = rec.get_appraisal_responsible_current_office()
            from_email = responsible and responsible.email or False
            
            email_template = self.env.ref(
                    'nl_appraisal.appraisal_notify_template')
            body_html = _("""
                    Dear %s <br/><br/>
                    Below is the link for the performance appraisal for %s. This has been forwarded to you for your review and feedback. 
                    Kindly use the link below to access it and provide your feedback in the section available to you.
                    <br/>
                    <br/>
                    <a href="/supervisor/employee-appraisals/%s" class="btn" style="background-color: #875a7b; color: white;">View Appraisal</a>
                    <br/><br/>
                    Kind regards,
                    <br/>
                    HR Unit, SCA
                """) % (rec.second_manager_id.name, rec.employee_id.name, rec.id)
            if email_template:
                email_template.sudo().write({
                    'email_from': from_email,
                    'partner_to': reciever_user.partner_id and reciever_user.partner_id.id or '',
                    'email_to': not reciever_user.partner_id and reciever_user.email or '',
                    'subject': "Appraisal Second Supervisor Review",
                    'body_html': body_html,
                    })
                email_template.send_mail(rec.id, force_send=True)


class EmployeeAppriasalDiscussion(models.Model):
    _name = 'employee.appraisal.discussion'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
    _description = "Employee Appraisal Discussion and Events"
    
    name = fields.Char("Subject", required=True, tracking=True)
    discussion_date = fields.Date("Date", required=True, trcking=True)
    description = fields.Char(tracking=True)
    result = fields.Text(string="Result/Conclusion", tracking=True)
    attachment_id = fields.Binary()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
        ], default='draft')
    appraisal_id = fields.Many2one("employee.appraisal")
    line_ids = fields.One2many(
        comodel_name = 'employee.appraisal.discussion.lines',
        inverse_name = "discussion_id",
        )
    
    def move_to_in_progress(self):
        for rec in self:
            rec.state = 'in_progress'
    def move_to_done(self):
        for rec in self:
            rec.state = 'done'
        

class EmployeeAppraisalDiscussionLine(models.Model):
    _name = 'employee.appraisal.discussion.lines'
    _description = "Employee Appraisal Discussion and Events Lines"

    name = fields.Char("Item", required=True)
    discussion_line_date = fields.Date("Date", required=True)
    discussion_id = fields.Many2one('employee.appraisal.discussion')

class CalendarEvent(models.Model):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'

    @api.model_create_multi
    def create(self, vals_list):
        events = super().create(vals_list)
        for event in events:
            if event.res_model == 'employee.appraisal':
                appraisal = self.env['employee.appraisal'].browse(event.res_id)
                if appraisal.exists():
                    appraisal.write({
                        'meeting_id': event.id,
                        'date_final_interview': event.start_date if event.allday else event.start
                    })
        return events


# class EmployeeAppraisal(models.Model):
#     _inherit = 'hr.employee'

#     has_valid_appraisal = fields.Boolean(compute='_compute_has_valid_appraisal')
#     appraisal_ids = fields.One2many("employee.appraisal", 'employee_id')

#     def _compute_has_valid_appraisal(self):
#         for rec in self:
#             valid_appraisal_record = rec.appraisal_ids.search([
#                 ("employee_id", '=', rec.id), 
#                 ("state", "not in", ['cancel', 'draft', 'objective_setting']),
#                 ('review_period_start_date', '<=', date.today().strftime("%Y-12-31")),
#                 ('review_period_start_date', '>=', date.today().strftime("%Y-01-01")),
#             ], limit=1)
#             rec.has_valid_appraisal = True if valid_appraisal_record else False