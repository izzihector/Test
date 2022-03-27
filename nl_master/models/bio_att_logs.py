# -*- coding: utf-8 -*-

from odoo import fields, models,api
from odoo.exceptions import ValidationError
# from datetime import datetime, date, timedelta


class HrAttendanceLogs(models.Model):
    _name = 'hr.attendance.logs'
    _description = 'HR Attendance Logs'

    name = fields.Text(string="Message")
    ip_address = fields.Char(String="IP Address")