# -*- coding: utf-8 -*-

import pytz
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class EmployeeFleet(models.Model):
    _name = 'employee.fleet'
    _description = 'Vehicle Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _get_employee_id_domain(self):
        res = [('id', '=', 0)]
        if self.user_has_groups('fleet.fleet_group_manager') or self.user_has_groups('fleet.fleet_group_user'):
            res = "[]"
        elif self.env.user.employee_ids:
            employee = self.env.user.employee_ids[0]
            res = [('id', '=', employee.id), '|', ('company_id', '=',
                                                   False), ('company_id', '=', employee.company_id.id)]
        return res

    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Requested'),
        ('confirm', 'Confirmed'),
        ('reject', 'Rejected'),
        ('cancel', 'Cancelled')
    ], string="State", default="draft")
    name = fields.Char(
        string="Request Number",
        copy=False
    )
    employee = fields.Many2one(
        'hr.employee',
        string="Requested By",
        required=1,
        domain=lambda self: self._get_employee_id_domain()
    )
    request_date = fields.Date(
        string="Requested Date",
        default=fields.Date.context_today,
        required=1,
        help="Request Date"
    )
    date_from = fields.Datetime(
        string="From",
        required=1
    )
    date_to = fields.Datetime(
        string="To",
        required=1
    )
    purpose = fields.Text(
        string="Purpose",
        required=1,
        help="Purpose"
    )
    trip_type = fields.Selection([
        ('one', 'One Way'),
        ('round', 'Round Trip')
    ], string="Trip Type")
    pickup_location = fields.Char(
        string="Pickup Location"
    )
    drop_location = fields.Char(
        string="Drop Location"
    )
    vehicle_type = fields.Selection([
        ('normal', 'Normal'),
        ('armored', 'Armored')
    ], string="Vehicle Type")

    employee_ids = fields.Many2many(
        string="Employee Lines",
        comodel_name='hr.employee',
        relation='employee_ids_rel',
        help="To add more Employee in Vehicle!"
    )
    fleet = fields.Many2one(
        'fleet.vehicle',
        string="Vehicle"
    )
    driver_id = fields.Many2one(
        'res.partner',
        related='fleet.driver_id',
        string="Driver"
    )

    def _get_from_and_to_timestamp_as_utc(self, date):
        mytz = pytz.timezone(self._context.get('tz') or self.env.user.tz)
        display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(
            str(date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(mytz), "%Y-%m-%d %H:%M:%S")

        return display_date_result

    def _get_trip_type(self, trip_type):
        if trip_type == 'round':
            return 'Round Trip'
        elif trip_type == 'one':
            return 'One Way'
        else:
            return ''

    def _compute_active_groups(self):
        if self.env.user.has_group('fleet.fleet_group_manager'):
            self.active_groups = True
        else:
            self.active_groups = True
            if self.state != 'draft':
                self.active_groups = False

    active_groups = fields.Boolean(
        compute='_compute_active_groups',
        default=True,
        string="Active Groups"
    )

    def _count_passengers(self):
        self.no_of_passenger = self.employee_ids.search_count([])

    no_of_passenger = fields.Integer(
        compute='_count_passengers',
        string="No of Passanger"
    )

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('employee.fleet')
        return super(EmployeeFleet, self).create(vals)

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(
                    _("You can not delete in %s state!") % record.state)
        return super(EmployeeFleet, self).unlink()

    @api.constrains('date_from', 'date_to')
    def onchange_date_to(self):
        for each in self:
            if each.date_from > each.date_to:
                raise Warning(
                    _('Date To must be greater than Date From'))

    def _mail_vehicle(self):
        user = self.env['res.users']
        from_mail = user.browse(self._uid) and user.login or ''
        from_mail = from_mail.encode('utf-8')
        to_mail = (self.employee.work_email).encode('utf-8')

        email_template = False
        message = ""
        if self.env.context.get('confirm'):
            email_template = self.env.ref(
                'nl_vehicle_request.confirm_vehicle_request')
            message = "Approved"

        if self.env.context.get('cancel'):
            email_template = self.env.ref(
                'nl_vehicle_request.reject_vehicle_request')
            message = "Rejected"

        vehicle = " "
        driver = " "
        if self.fleet:
            vehicle = self.fleet.name
        if self.driver_id:
            driver = self.driver_id.name

        body_html = """
            <![CDATA[<div style="font-family: 'Lucica Grande',
            Ubuntu, Arial, Verdana, sans-serif; font-size: 14px;
            color: rgb(34, 34, 34); background-color: #FFF; ">
            <p>Dear """ + self.employee.name + """,</p>
            <p>Your vehicle request for the reference """ + self.name + """ is """ + message + """.
            <br/>
            <ul>
                <li>Vehicle: """ + vehicle + """</li>
                <li>Driver: """ + driver + """</li>
            </ul>
            <br/>
            <br/>
            <p>Thank you.<br/>
            </p>
        """
        if email_template:
            email_template.sudo().write({
                'body_html': body_html,
                'email_from': from_mail,
                'email_to': to_mail
            })
            email_template.send_mail(self.id, force_send=True)

    def activity_update(self):
        note = _('New %s Request created by %s from %s to %s') % (
            self.employee.name, self.create_uid.name, fields.Datetime.to_string(
                self.date_from), fields.Datetime.to_string(self.date_to))
        groups = []
        user = self.env['res.users']
        groups.extend(user.search([]).filtered(
            lambda x: x.has_group("fleet.fleet_group_manager")).ids)
        users = list(set(groups))
        for login in users:
            manager = user.browse(login)
            self.activity_schedule(
                'nl_vehicle_request.mail_vehicle_approval',
                note=note,
                user_id=manager.id or self.env.user.id)

    def send(self):
        self.state = 'request'
        self.activity_update()

    def confirm(self):
        if not self.fleet:
            raise Warning(
                _("Select Vehicle for the reference %s") % self.name)
        self.state = 'confirm'
        self.with_context(confirm=True)._mail_vehicle()
        self.activity_unlink(['nl_vehicle_request.mail_vehicle_approval'])

    def reject(self):
        self.state = 'reject'
        self.with_context(cancel=True)._mail_vehicle()
        self.activity_unlink(['nl_vehicle_request.mail_vehicle_approval'])

    def cancel(self):
        if self.reserved_fleet_id:
            self.reserved_fleet_id.unlink()
        self.state = 'cancel'

    def returned(self):
        self.reserved_fleet_id.unlink()
        self.returned_date = fields.datetime.now()
        self.state = 'return'
