import distutils
from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError, AccessError
import xlsxwriter
from odoo.addons.nl_master.helpers import master_methods, master_data

from datetime import datetime
import base64
import os
from distutils import util

class ApplicantInterviewScore(models.TransientModel):
    _name = "hr.applicant.interview.score.wizard"
    _description = 'Applicant Interview Score Wizard'
    _rec_name = 'applicant_id'


    # interview_score = fields.Selection(
    #     [(str(val), str(val)) for val in range(0,11)]
    #     , required=True)
    interview_score = fields.Float(required=True)
    user_id = fields.Many2one('res.users', required=True, readonly=True)
    applicant_id = fields.Many2one('hr.applicant', required=True, readonly=True)

    def save_score(self):
        for rec in self:
            self.env['hr.applicant.interview.score'].create({
                'interview_score': rec.interview_score,
                'user_id': rec.user_id.id,
                'applicant_id': rec.applicant_id.id
                })