# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from odoo.osv import expression
from lxml import etree
from odoo import models, fields, api,_

import random
import string

import re


class HrUnit(models.Model):
    _name = 'hr.unit'
    _description = "Units"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "name"

    name = fields.Char('Unit')
    department_id = fields.Many2one('hr.department',stirng="Department")
    
    name_in_dari = fields.Char('نام')
    manager_id = fields.Many2one('hr.employee', string='Manager', tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    color = fields.Integer('Color Index')
    active = fields.Boolean('Active', default=True)
    member_ids = fields.One2many('hr.employee', 'unit_id', string='Members', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    