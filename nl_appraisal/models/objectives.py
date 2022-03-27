# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EmployeeAppriasalObjectives(models.Model):
    _name = 'employee.appraisal.objectives'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    name = fields.Char(
        string="Objective",
        required=True
        )
    employee_feedback = fields.Text()
    manager_feedback = fields.Text()
    expected_outcome = fields.Text()
    active = fields.Boolean(default=True)
    rating = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ])
    creteria = fields.Text()
    appraisal_id = fields.Many2one(
        comodel_name = "employee.appraisal"
        )
    individual_appraisal_id = fields.Many2one(
        comodel_name="employee.appraisal"
        )
    next_appraisal_id = fields.Many2one(
        comodel_name = "employee.appraisal"
        )


class ProbationAppriasalObjectives(models.Model):
    _name = 'probation.appraisal.objectives'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    name = fields.Char(
        string="Objective",
        required=True
        )

    expected_outcome = fields.Text(required=True)
    active = fields.Boolean(default=True)

    probation_appraisal_id = fields.Many2one(
        comodel_name = "probation.appraisal"
        )