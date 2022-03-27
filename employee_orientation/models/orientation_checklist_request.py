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

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class OrientationChecklistRequest(models.Model):
    _name = 'orientation.request'
    _description = "Employee Orientation Request"
    _rec_name = 'request_name'
    _inherit = 'mail.thread'

    request_name = fields.Char(string='Name')
    request_orientation = fields.Many2one('employee.orientation', string='Employee Orientation')
    employee_company = fields.Many2one('res.company', string='Company', required=True,
                                       default=lambda self: self.env.user.company_id)
    partner_id = fields.Many2one('res.users', string='Responsible User')
    request_date = fields.Date(string="Date")
    employee_id = fields.Many2one('hr.employee', string='Employee')
    request_expected_date = fields.Date(string="Expected Date")
    attachment_id_1 = fields.Many2many('ir.attachment', 'orientation_rel_1', string="Attachment")
    note_id = fields.Text('Description')
    user_id = fields.Many2one('res.users', string='users', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    state = fields.Selection([
        ('new', 'New'),
        ('cancel', 'Cancel'),
        ('complete', 'Completed'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='new')

    def confirm_send_mail(self):
        self.ensure_one()
        email_template = self.env.ref('employee_orientation.orientation_request_mailer')
        email_template.send_mail(self.id, force_send=True)

    def confirm_request(self):
        if self.env.user.has_group('hr.group_hr_user') or self.env.user.id == self.id:
            self.write({'state': "complete"})
        else:
            raise UserError("Only HR Officer or Responible user can complete the orientation request record.")

    def cancel_request(self):
        self.write({'state': "cancel"})
