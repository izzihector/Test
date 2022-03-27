# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Anusha @cybrosys(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, models, _, fields


class PackingReportValues(models.AbstractModel):
    _name = 'report.employee_orientation.print_pack_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        lst = []
        training_obj = self.env['employee.training'].search([('id', '=', data['res_id'])])

        if training_obj:
            for line in training_obj.employee_id:
                lst.append({
                    'name': line.name,
                    'gender_sub': 'her' if line.gender == 'female' else 'his',
                    'program_name': training_obj.program_name,
                    'company_name': training_obj.company_id.name,
                    'date_to': training_obj.date_to.strftime('%d-%m-%Y'),
                    'date_from': training_obj.date_from.strftime('%d-%m-%Y'),
                    'program_convener': training_obj.program_convener.name,
                    'duration': data['duration'],
                    'hours': data['hours'],
                    'minutes': data['minutes'],
                    'first_signatory': data['signatories']['first_signatory'],
                    'second_signatory': data['signatories']['second_signatory'],
                    'first_signatory_position': data['signatories']['first_signatory_position'],
                    'second_signatory_position': data['signatories']['second_signatory_position'],
                    'date': fields.Date.today().strftime('%d-%m-%Y')
                })

        return {
            'data': lst,
        }

