# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Kavya Raveendran (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
from datetime import date


class ReportCertificate(models.AbstractModel):
    _name = 'report.nl_employee.employee_certificate_template'
    _template = 'nl_employee.employee_certificate_template'

    @api.model
    def _get_report_values(self, docids, data=None):

        report_obj = self.env['ir.actions.report']

        report = report_obj._get_report_from_name('nl_employee.employee_certificate_template')

        docs = self.env['hr.employee'].browse(docids)

        contract = self.env['hr.contract'].search([('employee_id', 'in', docids)],)

        date_now = date.today().strftime('%Y %B %d')

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': docs,
            'contract': contract,
            'date': date_now,
        }
        return docargs
