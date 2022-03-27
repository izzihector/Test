from odoo import models, fields, api, _
from odoo import http
from odoo.http import request
from datetime import datetime, timedelta

import pytz
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ProductTemplate(models.Model):
    _inherit = 'hr.contract'

  

    @api.model
    def _cron_set_company_in_webkul_synced_products(self):
        print("N/A")
        
#         employee_ids = self.env['hr.employee'].sudo().search([])

#         for employee in employee_ids:
#             if employee.idc_no:
#                 if float(employee.skype) <= 2500:
#                     self.env['hr.contract'].sudo().create({
#                         'name':str(datetime.now().year) + ' / ' + employee.idc_no + ' /001',
#                         'employee_id':employee.id,
#                         'renewal_type':'new',
#                         'job_id':employee.job_id.id,
#                         'contract_approval_user':'ceo',
#                         'structure_type_id':1,
#                         'date_start':'2021-01-01',
#                         'wage':employee.skype,
#                         'salary_currency':'USD',
#                         'legal_leave':0,
#                         'sick_leave':0,
#                         'wage_afn':0.0,
#                         'grade':employee.personal_mobile


#                     })
#                 else:

#                     self.env['hr.contract'].sudo().create({
#                     'name':str(datetime.now().year) + ' / ' + employee.idc_no + ' /001',
#                     'employee_id':employee.id,
#                     'renewal_type':'new',
#                     'job_id':employee.job_id.id,
#                     'contract_approval_user':'ceo',
#                     'structure_type_id':1,
#                     'date_start':'2021-01-01',
#                     'wage':0.0,
#                     'salary_currency':'AFN',
#                     'legal_leave':0,
#                     'sick_leave':0,
#                     'wage_afn':employee.skype,
#                     'grade':employee.personal_mobile


#                 })
#             else:
#                 if float(employee.skype) <= 2500:
#                     self.env['hr.contract'].sudo().create({
#                         'name':str(datetime.now().year) + ' /001',
#                         'employee_id':employee.id,
#                         'renewal_type':'new',
#                         'job_id':employee.job_id.id,
#                         'contract_approval_user':'ceo',
#                         'structure_type_id':1,
#                         'date_start':'2021-01-01',
#                         'wage':employee.skype,
#                         'salary_currency':'USD',
#                         'legal_leave':0,
#                         'sick_leave':0,
#                         'wage_afn':0.0,
#                         'grade':employee.personal_mobile


#                     })
#                 else:

#                     self.env['hr.contract'].sudo().create({
#                         'name':str(datetime.now().year) + ' /001',
#                         'employee_id':employee.id,
#                         'renewal_type':'new',
#                         'job_id':employee.job_id.id,
#                         'contract_approval_user':'ceo',
#                         'structure_type_id':1,
#                         'date_start':'2021-01-01',
#                         'wage':0.0,
#                         'salary_currency':'AFN',
#                         'legal_leave':0,
#                         'sick_leave':0,
#                         'wage_afn':employee.skype,
#                         'grade':employee.personal_mobile


#                 })
