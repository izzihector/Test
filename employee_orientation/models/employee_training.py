# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Anusha @cybrosys(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    certificates = fields.Boolean(default=True, string="Certificates")
    training_id = fields.Many2one('employee.training')

class EmployeeTraining(models.Model):
    _name = 'employee.training'
    _rec_name = 'program_name'
    _description = "Employee Training"
    _inherit = 'mail.thread'

    program_name = fields.Char(string='Training Program', required=True)
    program_convener = fields.Many2one('res.users', string='Responsible User', size=32, required=True)
    mode = fields.Selection([
        ('employee', 'By Employee'),
        ('unit', 'By Unit'),
        ('department', 'By Department'),
        ('office', 'By Office')
    ], required=True, string = 'Participant\'s Mode')
    department_id = fields.Many2one('hr.department', string='Department')
    office_id = fields.Many2one('office', string='Office')
    unit_id = fields.Many2one('hr.unit', string='Unit')
    employee_id = fields.One2many('hr.employee', 'training_id', string='Employee Details')
    note_id = fields.Text('Description')
    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)
    user_id = fields.Many2one('res.users', string='users', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    venue = fields.Char(string='Training Venue', required=True)

    state = fields.Selection([
        ('new', 'New'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Canceled'),
        ('complete', 'Completed'),
        ('print', 'Print'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='new')

    @api.onchange('mode')
    def employee_details(self):
        self.unit_id = self.office_id = self.department_id = self.employee_id = False

    @api.onchange('department_id', 'office_id', 'unit_id')
    def onchange_category(self):
        field_id = 0
        field_name = ''
        if self.department_id:
            field_id = self.department_id.id
            field_name = 'department_id'
        elif self.office_id:
            field_id =self.office_id.id
            field_name = 'office_id'
        elif self.unit_id:
            field_id = self.unit_id.id
            field_name = 'unit_id'
        if field_id:
            self.employee_id = self.env['hr.employee'].search([(field_name, '=', field_id)])

    @api.constrains('date_from', 'date_to')
    def date_constrains(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_to < rec.date_from:
                raise ValidationError('The End date cannot be earlier than the start date')
    
    @api.onchange('date_from', 'date_to')
    def date_change(self):
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise ValidationError('The End date cannot be earlier than the start date')

    def print_event(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("employee_orientation.action_training_certificate_signatory_wizard")
        action.update({
            'context': {'default_training_id':self.id}
        })
        return action

    def complete_event(self):
        self.write({'state': 'complete'})

    def confirm_event(self):
        followers = [self.program_convener.partner_id.id]
        subtype_ids = self.env['mail.message.subtype'].search(
            [('res_model', '=', 'hr.applicant')]).ids
        self.message_subscribe(
            partner_ids=followers,
            subtype_ids=subtype_ids)
        self.write({'state': 'confirm'})

    def cancel_event(self):
        self.write({'state': 'cancel'})

    def confirm_send_mail(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('employee_orientation', 'orientation_training_mailer')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'employee.training',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def prepare_emails(self):
        for rec in self:
            return rec.program_convener.email+','+','.join([emp.work_email for emp in rec.employee_id if emp.work_email and emp.work_email != 'N/A'])

