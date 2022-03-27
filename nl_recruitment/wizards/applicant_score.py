import distutils
from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError, AccessError
import xlsxwriter
from odoo.addons.nl_master.helpers import master_methods, master_data

from datetime import datetime
import base64
import os
from distutils import util

class ApplicantScore(models.TransientModel):
    _name = "hr.applicant.score.wizard"
    _description = 'Applicant Score Wizard'
    _rec_name = 'applicant_id'


    shortlisting_score = fields.Selection(
        [(str(val), str(val)) for val in range(0,11)]
        , required=True)
    score_category = fields.Selection([
        ('poor', 'Poor'),
        ('below_exceptions', 'Below Expectations'),
        ('minor_shortfall', 'Minor Shortfall'),
        ('competent', 'Competent'),
        ('beyond_competent', 'Beyond Competent'),
        ], readonly=True)
    user_id = fields.Many2one('res.users', required=True, readonly=True)
    applicant_id = fields.Many2one('hr.applicant', required=True, readonly=True)


    @api.onchange('shortlisting_score')
    def compute_score_category(self):
        for rec in self:
            rec.score_category = False
            if rec.shortlisting_score:
                rec.score_category = master_data.SCORE_RANGE_DICT.get(rec.shortlisting_score)

    def save_score(self):
        for rec in self:
            self.env['hr.applicant.score'].create({
                'shortlisting_score': rec.shortlisting_score,
                'score_category': rec.score_category,
                'user_id': rec.user_id.id,
                'applicant_id': rec.applicant_id.id
                })