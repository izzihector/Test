# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models
from datetime import datetime

# calculate attendance duration


class HrAttendanceDuration(models.Model):
    _inherit = "hr.attendance"

    att_duration = fields.Float("Duration")

    # find employee working time duration.
    def write(self, vals):
        if vals.get("check_out", False):
            date1 = str(self.check_in)
            datetimeformat = "%Y-%m-%d %H:%M:%S"
            date2 = str(vals.get("check_out"))
            date11 = datetime.strptime(date1, datetimeformat)
            date12 = datetime.strptime(date2, datetimeformat)
            timedelta = date12 - date11
            tot_sec = timedelta.total_seconds()
            hour = tot_sec//3600
            minutes = (tot_sec % 3600) // 60
            duration_hour = ("%d.%d" % (hour, minutes))
            vals.update({"att_duration": float(duration_hour)})

        return super(HrAttendanceDuration, self).write(vals)
