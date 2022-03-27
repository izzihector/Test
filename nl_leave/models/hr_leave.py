# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools, exceptions
from datetime import datetime, date
from odoo.exceptions import UserError
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.addons.resource.models.resource import HOURS_PER_DAY

from odoo.tools.translate import _
from odoo.tools.float_utils import float_round
from dateutil.relativedelta import relativedelta
from odoo.addons.nl_master.helpers import master_methods

class HolidaysRequest(models.Model):
    _inherit = "hr.leave"
    _order = "create_date desc"
    
    # modified the validationerror message to show employee's name

    leave_attachment = fields.Binary(
        string='Attachments')
    allocation_details = fields.Html(compute="_onchange_employee_id_get_allocations")
    is_attachment_required = fields.Boolean(related="holiday_status_id.require_attachments", store=True)
    unit_id = fields.Many2one('hr.unit', compute='_compute_unit_id', store=True, readonly=False, string='Unit')


    @api.depends('employee_id')
    def _onchange_employee_id_get_allocations(self):
        for rec in self:
            rec.allocation_details = ''
            if rec.employee_id:
                timeoffs = self.env['hr.leave.type'].sudo().with_context(employee_id=int(rec.employee_id)).search([])
                data = """
                        <div>
                    """
                for timeoff in timeoffs:
                    data += f""" 
                        <div class="row">
                            <div class="col-lg-6"><strong>{timeoff.name}</strong>:</div><div class="col-lg-6">{ timeoff.virtual_leaves_taken } / { timeoff.max_leaves }</div>
                        </div> 
                    """
                data += "</div>"
                rec.allocation_details = data

    @api.constrains('date_from', 'date_to', 'state', 'employee_id')
    def _check_date(self):
        for holiday in self:
            
            if not holiday.employee_id.join_date:
                raise ValidationError(_("Employee does not have employment date. Please add employment date first. "))

            if holiday.employee_id and holiday.date_from and holiday.date_from.date() < holiday.employee_id.join_date:
                raise ValidationError(_("You cannot set a time off prior to the employment start date."))

            domain = [
                ('date_from', '<', holiday.date_to),
                ('date_to', '>', holiday.date_from),
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(_(f'You can not set 2 time off that overlaps on the same day for the {self.employee_id.name} .', ))

    @api.depends('employee_id')
    def _compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.employee_id and rec.employee_id.unit_id or False

    def ceo_second_approval_mail(self):
        user = self.env['res.users']
        from_mail = user.browse(self._uid) and user.login or ''
        from_mail = from_mail.encode('utf-8')

        groups = []

        groups.extend(user.search([]).filtered(
            lambda x: x.has_group("nl_contract.group_ceo")).ids)
        users = list(set(groups))

        for login in users:
            ceo = user.browse(login)
            if ceo.work_email:
                to_mail = (ceo.work_email).encode('utf-8')

                email_template = self.env.ref(
                    'nl_leave.mail_second_approval_required')

                employee = ""
                department = ""
                position = ""
                if self.employee_id:
                    employee = self.employee_id.name
                if self.department_id:
                    department = self.department_id.name
                if self.employee_id.job_id:
                    self.employee_id.job_id.name

                body_html = """
                    <![CDATA[<div style="font-family: 'Lucica Grande',
                    Ubuntu, Arial, Verdana, sans-serif; font-size: 14px;
                    color: rgb(34, 34, 34); background-color: #FFF; ">
                    <p>Dear """ + ceo.name + """,</p>
                    <p>Employee """ + self.employee_id.name + """ whose details are listed below, has submitted a leave request exceeding normal leave periods. The leave request requires your approval.
                    <br/>
                    <ul>
                        <li>Employee Name: """ + employee + """</li>
                        <li>Department: """ + department + """</li>
                        <li>Position: """ + position + """</li>
                    </ul>
                    <br/>
                    </p>
                    <p>Thank you.<br/>
                """
                if email_template:
                    email_template.sudo().write({
                        'body_html': body_html,
                        'email_from': from_mail,
                        'email_to': to_mail
                    })
                    email_template.send_mail(self.id, force_send=True)


    def activity_update(self):
        groups = []
        user = self.env['res.users']
        groups.extend(user.search([]).filtered(
            lambda x: x.has_group("nl_contract.group_ceo")).ids)
        users = list(set(groups))
        to_clean, to_do = self.env['hr.leave'], self.env['hr.leave']
        for holiday in self:
            note = _('New %s Request created by %s from %s to %s') % (holiday.holiday_status_id.name, holiday.create_uid.name, fields.Datetime.to_string(holiday.date_from), fields.Datetime.to_string(holiday.date_to))
            if holiday.state == 'draft':
                to_clean |= holiday
            elif holiday.state == 'confirm':
                holiday.activity_schedule(
                    'hr_holidays.mail_act_leave_approval',
                    note=note,
                    user_id=holiday.sudo()._get_responsible_for_approval().id or self.env.user.id)
            elif holiday.state == 'validate1':
                for login in users:
                    ceo = user.browse(login)
                    holiday.activity_feedback(['hr_holidays.mail_act_leave_approval'])
                    holiday.activity_schedule(
                        'hr_holidays.mail_act_leave_second_approval',
                        note=note,
                        user_id=ceo.id or self.env.user.id)
            elif holiday.state == 'validate':
                to_do |= holiday
            elif holiday.state == 'refuse':
                to_clean |= holiday
        if to_clean:
            to_clean.activity_unlink(['hr_holidays.mail_act_leave_approval', 'hr_holidays.mail_act_leave_second_approval'])
        if to_do:
            to_do.activity_feedback(['hr_holidays.mail_act_leave_approval', 'hr_holidays.mail_act_leave_second_approval'])


    def action_approve(self):
        # if validation_type == 'both': this method is the first approval approval
        # if validation_type != 'both': this method calls action_validate() below
        if any(holiday.state != 'confirm' for holiday in self):
            raise UserError(_('Time off request must be confirmed ("To Approve") in order to approve it.'))

        current_employee = self.env.user.employee_id
        self.filtered(lambda hol: hol.validation_type == 'both').write({'state': 'validate1', 'first_approver_id': current_employee.id})


        # Post a second message, more verbose than the tracking message
        if not self.env.context.get('ignore_logs', False):
            for holiday in self.filtered(lambda holiday: holiday.employee_id.user_id):
                holiday.message_post(
                    body=_(
                        'Your %(leave_type)s planned on %(date)s has been accepted',
                        leave_type=holiday.holiday_status_id.display_name,
                        date=holiday.date_from
                    ),
                    partner_ids=holiday.employee_id.user_id.partner_id.ids)

        self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
        if not self.env.context.get('leave_fast_create') or not self.env.context.get('ignore_logs'):
            self.activity_update()
        return True

    @api.onchange('request_date_from_period', 'request_hour_from', 'request_hour_to',
                  'request_date_from', 'request_date_to',
                  'employee_id')
    def _onchange_request_parameters(self):
        if not self.request_date_from:
            self.date_from = False
            return

        if self.request_unit_half or self.request_unit_hours:
            self.request_date_to = self.request_date_from

        if not self.request_date_to:
            self.date_to = False
            return
    

    def leave_end_date(self):
        leaves = self.search([('state', 'not in', ['cancel', 'refuse'])])
        for leave in leaves:
            to_date = datetime.strptime(master_methods._get_full_date_from_timestamp(self._context.get('tz') or self.env.user.tz, leave.date_to), "%Y-%m-%d %H:%M:%S").date()
            if leave.request_date_to != to_date:
                old_state = leave.state
                number_of_days = leave.number_of_days
                leave.state = 'confirm'
                leave._compute_date_from_to()
                # if not leave.number_of_days:
                leave.number_of_days = number_of_days

                if old_state == 'validate':
                    leave.with_context(ignore_logs=True).action_approve()
                    if leave.state != 'validate':
                        leave.action_validate()
                else:
                    leave.state = old_state

class HolidaysType(models.Model):
    _name = "hr.leave.type"
    _inherit = ['hr.leave.type', 'mail.thread','mail.activity.mixin','resource.mixin']


    # Allocation
    default_allocation_days = fields.Float('Default Allocation Days')
    maximum_transfer = fields.Float('Maximum Allocation Transfer')
    include_in_leave_allocation_balance = fields.Boolean('Stop Accrual on this leave type')
    
    #Time Off
    maximum_time_off_days = fields.Float('Maximum Days per Request')
    gender = fields.Selection([('male', 'Male'),('female', 'Female')])
    time_request_applicablity = fields.Selection([
        ('after_porbation','After Probation'),
        ('after_specific_year','After Specific Year(s)')
        
    ], string="Grand Time Off After")
    after_specific_years = fields.Boolean('Number of Year(s)')


    require_attachments = fields.Boolean(string="Requires Attachment")
    require_attachments_after_days = fields.Float(string="Require Attachment After")

    
    default_allocation = fields.Boolean(default=True)
    default_allocation_type = fields.Selection([('regular', 'Regular'), ('accrual', ('Accrual'))], default="regular")
    
    leave_code =  fields.Char(required=True)
    # Fields for leave carry over
    allow_carry_over = fields.Boolean(
        string = "Allow Carry Over",
        defult = True
        )

    @api.constrains("leave_code")
    def validate_leave_code(self):
        self.ensure_one()
        if self.leave_code:
            if self.env['hr.leave.type'].search([('leave_code', '=', self.leave_code), ('id', '!=', self.id)]):
                raise ValidationError(_("Leave code must be unique."))


class ResourceMixinInherit(models.AbstractModel):
    _inherit = "resource.mixin"

    def copy_data(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if not self.resource_id:
            resource_vals = {'name': self._rec_name}
            tz = self.env['resource.calendar'].browse(self.resource_calendar_id.id).tz
            if tz:
                resource_vals['tz'] = tz
            resource = self.env['resource.resource'].create(resource_vals)
            self.write({'resource_id': resource.id})
        return super(ResourceMixinInherit, self).copy_data(default)

class HrLeave(models.Model):
    _inherit = 'hr.leave'
    
    @api.constrains('date_from', 'date_to')
    def _check_contracts(self):
        """
            A leave cannot be set across multiple contracts.
            Note: a leave can be across multiple contracts despite this constraint.
            It happens if a leave is correctly created (not accross multiple contracts) but
            contracts are later modifed/created in the middle of the leave.
        """
        for holiday in self:
            domain = [
                ('employee_id', '=', holiday.employee_id.id),
                ('date_start', '<=', holiday.date_to),
                '|',
                ('state', 'not in', ['draft', 'cancel','foreshorten','rejected']),
                '&',
                ('state', '=', 'draft'),
                ('kanban_state', '=', 'done'),
                '|',
                    ('date_end', '>=', holiday.date_from),
                    '&',
                        ('date_end', '=', False),
                        ('state', '!=', 'close')
            ]
            nbr_contracts = self.env['hr.contract'].sudo().search_count(domain)
            if nbr_contracts > 1:
                raise ValidationError(_('A leave cannot be set across multiple contracts.'))

class LeaveReportExtended(models.Model):
    _name = "hr.leave.report.all"
    _description = 'Time Off Summary / Report'
    _auto = False
    _order = "date_from DESC, employee_id"

    employee_id = fields.Many2one('hr.employee', string="Employee", readonly=True)
    name = fields.Char('Description', readonly=True)
    number_of_days = fields.Float('Number of Days', readonly=True)
    leave_type = fields.Selection([
        ('allocation', 'Allocation Request'),
        ('request', 'Time Off Request')
        ], string='Request Type', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True)
    category_id = fields.Many2one('hr.employee.category', string='Employee Tag', readonly=True)
    holiday_status_id = fields.Many2one("hr.leave.type", string="Leave Type", readonly=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
        ], string='Status', readonly=True)
    holiday_type = fields.Selection([
        ('employee', 'By Employee'),
        ('category', 'By Employee Tag')
    ], string='Allocation Mode', readonly=True)
    date_from = fields.Datetime('Start Date', readonly=True)
    date_to = fields.Datetime('End Date', readonly=True)
    payslip_status = fields.Boolean('Reported in last payslips', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'hr_leave_report_all')

        x = self._cr.execute("""
            CREATE or REPLACE view hr_leave_report_all as (
                SELECT row_number() over(ORDER BY leaves.employee_id) as id,
                leaves.employee_id as employee_id, leaves.name as name,
                leaves.number_of_days as number_of_days, leaves.leave_type as leave_type,
                leaves.category_id as category_id, leaves.department_id as department_id,
                leaves.holiday_status_id as holiday_status_id, leaves.state as state,
                leaves.holiday_type as holiday_type, leaves.date_from as date_from,
                leaves.date_to as date_to, leaves.payslip_status as payslip_status
                from (select
                    allocation.employee_id as employee_id,
                    allocation.private_name as name,
                    allocation.number_of_days as number_of_days,
                    allocation.category_id as category_id,
                    allocation.department_id as department_id,
                    allocation.holiday_status_id as holiday_status_id,
                    allocation.state as state,
                    allocation.holiday_type,
                    null as date_from,
                    null as date_to,
                    FALSE as payslip_status,
                    'allocation' as leave_type
                from hr_leave_allocation as allocation
                union all select
                    request.employee_id as employee_id,
                    request.private_name as name,
                    (request.number_of_days * -1) as number_of_days,
                    request.category_id as category_id,
                    request.department_id as department_id,
                    request.holiday_status_id as holiday_status_id,
                    request.state as state,
                    request.holiday_type,
                    request.date_from as date_from,
                    request.date_to as date_to,
                    request.payslip_status as payslip_status,
                    'request' as leave_type
                from hr_leave as request) leaves
            );
        """)
       

    def _read_from_database(self, field_names, inherited_field_names=[]):
        if 'name' in field_names and 'employee_id' not in field_names:
            field_names.append('employee_id')
        super(LeaveReportExtended, self)._read_from_database(field_names, inherited_field_names)
        if 'name' in field_names:
            if self.user_has_groups('hr_holidays.group_hr_holidays_user'):
                return
            current_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
            for record in self:
                emp_id = record._cache.get('employee_id', [False])[0]
                if emp_id != current_employee.id:
                    try:
                        record._cache['name']
                        record._cache['name'] = '*****'
                    except Exception:
                        # skip SpecialValue (e.g. for missing record or access right)
                        pass

    @api.model
    def action_time_off_analysis_extended(self):
        
        
        return {
            'name': _('Time Off Analysis'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave.report.all',
            'view_mode': 'tree,form,pivot',
            'search_view_id': self.env.ref('nl_leave.view_hr_holidays_filter_report_extended').id,
            'domain': [('state','=','validate')],
         
            'context': {
                'search_default_group_employee': True,
                'search_default_group_type': True,


            }
        }

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if not self.user_has_groups('hr_holidays.group_hr_holidays_user') and 'name' in groupby:
            raise exceptions.UserError(_('Such grouping is not allowed.'))
        return super(LeaveReportExtended, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

