# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError



class HrPayslipComputation(models.Model):
    _name = 'hr.payroll.computation'
    
    name = fields.Many2one('hr.employee', 'Employee')

    active = fields.Boolean("Active", default=True)

    rule_id = fields.Many2one('hr.salary.rule', 'Computation')

    amount = fields.Float('Amount')

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



class EmployeePayslipAttendanceHours(models.Model):
    _name = 'employee.payslip.attendance'

    employee_id = fields.Many2one('hr.employee')

    description = fields.Char("Description")
    late_check_in_hours = fields.Float("Late Checkin")
    early_check_out_hours = fields.Float("Early Checkout")
    total_not_same_day_check_out = fields.Float("Total Not Same Day Checkout")
    early_check_in_hours = fields.Float("Early Checkin")
    date = fields.Char("Date")
    late_check_out_hours = fields.Float("Late Checkout")
    total_not_check_out = fields.Float("Total Not Checkout")
    total_not_check_in = fields.Float("Total Not Checkin")
    payslip_id = fields.Many2one(
        'hr.payslip'
    )
