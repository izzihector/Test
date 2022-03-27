# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict
import pytz
from datetime import datetime, date, time

class HrPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _inherit = ['hr.payslip.run','mail.thread','mail.activity.mixin','resource.mixin']
    
    payslip_pending_employees = fields.One2many('employees.pending','payslip_run_id', string="Pending Employees", )
    employee_pending_count = fields.Integer(compute="_payroll_employee_pending_count")
    master_batch_id = fields.Many2one('generate.payroll.master')
    office_id = fields.Many2one('office', string="Office")
    calculate_attendance = fields.Selection([
        ('1','Attendance'),
        ('2','Manual'),
        ('3',"Skip Attendance")
    ],string="Calculate Attendance Based on", required=True)

    def action_close(self):
        if self._are_payslips_ready():
            self.write({'state' : 'cancel'})
            return
   
    def _are_payslips_ready(self):
        return all(slip.state in ['cancel'] for slip in self.mapped('slip_ids'))
    def _payroll_employee_pending_count(self):
        # employee_pending = self.env['employees.pending'].search([('payslip_run_id','=',self.id)])
        self.employee_pending_count = len(self.payslip_pending_employees)
    
    def action_view_employee_pending(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Employee Pending',
            'view_mode': 'tree,form',
            'res_model': 'employees.pending',
            'domain': [('payslip_run_id', '=', self.id)],
        }

    month = fields.Selection([
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),

    ])

    state = fields.Selection([
        ('draft', 'Draft'),
        ('hr','HR Review'),
        ('finance','Finance Review'),
        ('verify', 'Waiting'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        
    ], string='Status',  index=True, readonly=True, copy=False, default='draft',track_visibility=True,
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is under verification, the status is \'Waiting\'.
                \n* If the payslip is confirmed then status is set to \'Done\'.
                \n* When user cancel payslip the status is \'Rejected\'.""")

    def action_send_payslip_email(self):
        for record in self:
            slip_ids = self.env['hr.payslip'].search([('id', 'in', record.slip_ids.ids)])
            for ids in slip_ids:
                payslip = self.env['hr.payslip'].browse(int(ids))
                payslip.nl_payslip_mail(payslip.employee_id, record.date_end)

    def get_user(self):
        for record in self:
            slip_ids = self.env['hr.payslip'].search([('id', 'in', record.slip_ids.ids)])
            for ids in slip_ids:
                payslip = self.env['hr.payslip'].browse(int(ids))
                payslip.nl_payslip_mail(payslip.employee_id, record.date_end)


    def action_submit_to_finance(self):
        self.state = 'finance'
        self.slip_ids.filtered(lambda slip: slip.state != 'cancel').change_payslip_state_to_finance()

    def action_set_as_draft(self):
        self.state = 'draft'
        self.slip_ids.filtered(lambda slip: slip.state != 'cancel').set_payslips_as_draft()