# -*- coding: utf-8 -*-
from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


class ContractSignatory(models.TransientModel):
    _name = "training.signatory"
    _description = 'Training Certificate Signatory'

    training_id = fields.Many2one('employee.training')
    first_signatory = fields.Many2one('res.users',string="First Signatory")
    second_signatory = fields.Many2one('res.users',string="Second Signatory")
    

    def print_training_certificate(self):
        self.ensure_one()
        duration = (self.training_id.date_to - self.training_id.date_from).days
        pause = relativedelta(hours=0)
        difference = relativedelta(self.training_id.date_to, self.training_id.date_from) - pause
        hours = difference.hours
        minutes = difference.minutes
        data = {
            'duration': duration,
            'hours': hours,
            'minutes': minutes,
            'res_id': self.training_id.id,
            'signatories': {
                'first_signatory': self.first_signatory and self.first_signatory.name or False,
                'second_signatory': self.second_signatory and self.second_signatory.name or False,
                'first_signatory_position': self.first_signatory and self.first_signatory.employee_id and self.first_signatory.employee_id.job_id and self.first_signatory.employee_id.job_id.name or False,
                'second_signatory_position': self.second_signatory and self.second_signatory.employee_id and self.second_signatory.employee_id.job_id and self.second_signatory.employee_id.job_id.name or False
            }
        }
        return self.env.ref('employee_orientation.print_pack_certificates').report_action(self, data=data)
