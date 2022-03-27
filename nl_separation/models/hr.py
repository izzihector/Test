# -*- coding: utf-8 -*-

from odoo import models, api, fields
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    resign_date = fields.Date(
        string='Resign Date',
        groups="hr.group_hr_user",
        help="A employee resign date"
    )
    last_date = fields.Date(
        string='Last Date',
        groups="hr.group_hr_user",
        help="A last date of employee"
    )
    check_date = fields.Boolean(
        compute='_cal_date',
        method=True,
        String="Checking Date",
        groups="hr.group_hr_user"
    )
    experience = fields.Char(
        string="Experience",
        groups="hr.group_hr_user"
    )

    def _cal_date(self):
        check = False
        separation_model = self.env['hr.separation']
        for emp in self:
            sep_ids = separation_model.search([
                ('employee_id', '=', emp.id)
            ])
            for sep in sep_ids:
                if sep.state == 'approve':
                    check = True
            emp.check_date = check

    @api.onchange('resign_date')
    def cal_last_date(self):
        # This method calculates the last date based on the notice period
        if self.resign_date:
            r_date = self.resign_date
            l_date = r_date + relativedelta(months=2)
            self.last_date = l_date.strftime(DEFAULT_SERVER_DATE_FORMAT)

    @api.onchange('last_date')
    def cal_date_change(self):
        if self.last_date and self.join_date:
            l_date = self.last_date
            j_date = self.join_date
            delta = relativedelta(l_date, j_date)
            if delta.days + 1 >= 15:
                delta.months = delta.months + 1
            str_date = str(delta.years) + " " + 'Year' + " " + \
                str(delta.months) + " " + 'Month'
            self.experience = str_date
        else:
            self.experience = None
