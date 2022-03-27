# -*- coding: utf-8 -*-

from odoo import fields, models,api


class LateHoursException(models.Model):
    _name = "late.hours.exception"

    date = fields.Date(required=True, string='Date')
    skip_late_check_in = fields.Boolean(string='Skip Late Check In')
    skip_early_check_out = fields.Boolean(string='Skip Early Checkout')
    calendar_id = fields.Many2one(comodel_name='resource.calendar')


    _sql_constraints = [
        ('unique_date', 'UNIQUE(date)',
            'Current date already configured!')]


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    late_hours_exception_ids = fields.One2many(comodel_name='late.hours.exception', inverse_name='calendar_id')

