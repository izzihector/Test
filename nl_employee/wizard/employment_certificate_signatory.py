import distutils
from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError, AccessError
import xlsxwriter
from odoo.addons.nl_master.helpers import master_methods, master_data

from datetime import datetime
import base64
import os
from distutils import util

class ContractSignatory(models.TransientModel):
    _name = "employment.certificate.signatory"
    _description = 'Employment Certificate Signatory'

    employee_id = fields.Many2one('hr.employee')
    first_signatory = fields.Many2one('res.users',string="First Signatory")
    second_signatory = fields.Many2one('res.users',string="Second Signatory")


    def print_employment_certificate(self):
        data = {
            'model': 'hr.employee',
            'form': self.read()[0],
        }
        contracts = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id)],order='create_date desc')
        value_lists = []
        print("+++++++++++=",contracts)
        employee_vals = {
            'name':self.employee_id.name,
            'father_name':self.employee_id.father_name,
            'gender':self.employee_id.gender,
            'first_signatory':self.first_signatory.name,
            'first_signatory_position':self.first_signatory.employee_id.job_id.name,
            'second_signatory':self.second_signatory.name,
            'second_signatory_position':self.second_signatory.employee_id.job_id.name,
            'company':self.employee_id.company_id.name,
            'date':fields.Date.today(),
        }
        for contract in contracts:
            contract_vals = {
                    'position':contract.job_id.name,
                    'date_start':contract.date_start,
                    'date_end':contract.date_end,
                    'state':contract.state,
                    'separation_date':contract.separation_date,
                    'date_end': contract.date_end,
                    'foreshorten_cancellation_date':contract.foreshorten_cancellation_date,
                }
            value_lists.append(contract_vals)
        data['certificate'] = value_lists
        data['employee'] = [employee_vals]

        return self.env.ref('nl_employee.employee_certificate').report_action(self, data=data)