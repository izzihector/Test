import datetime

from odoo import models, fields, api, _
from odoo import fields
from odoo import http
import base64
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

from datetime import datetime, time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, DEFAULT_SERVER_DATETIME_FORMAT as DTF

from odoo.tools.translate import _

from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.exceptions import AccessError, MissingError


class AppraisalPortal(CustomerPortal):

    def _prepare_home_portal_values(self,counters):
        values = super(AppraisalPortal, self)._prepare_home_portal_values(counters)
        appraisal_count = request.env['employee.appraisal'].sudo().search_count([('employee_id','=',request.env.user.employee_id.id)])
        values.update({
            'appraisal_count': appraisal_count,

        })
        return values

    @http.route('/employee/appraisal/start', type='http', auth="user", website=True)
    def start_employee_appriasal(self, **kw):

        appraisal_id = request.env['employee.appraisal'].sudo().search([('token','=',kw.get('token'))])

        return request.render("nl_appraisal.portal_employee_apprisal_start",appraisal_id)