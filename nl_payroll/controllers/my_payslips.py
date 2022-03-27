import datetime

from odoo import models, fields, api, _
from odoo import fields
from odoo import http
import base64
import random
import string
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

from datetime import datetime, time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, DEFAULT_SERVER_DATETIME_FORMAT as DTF

from odoo.tools.translate import _

from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.exceptions import AccessError, MissingError


class WebsiteAccount(CustomerPortal):
    
    def _prepare_portal_layout_values(self):
        values = super(WebsiteAccount, self)._prepare_portal_layout_values()
        payslip_count = request.env['hr.payslip'].sudo().search_count([('employee_id','=',request.env.user.employee_id.id),('state','=','done')])
        print(payslip_count)
        values.update({
            'payslip_count': payslip_count,
        })
        return values


    def get_domain_my_payslips(self, user):
        # user => logged in user
        payslips = request.env['hr.payslip'].sudo().search([('employee_id', '=',request.env.user.employee_id.id),('state','=','done')])

        payslip_ids = []
        for item in payslips:
            payslip_ids.append(item.id)

        return [
            ('id', 'in', payslip_ids),
        ]

    @http.route(['/my/payslips/list', '/my/payslips/list/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_payslips(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        HrPayslips = request.env['hr.payslip']
        domain = self.get_domain_my_payslips(request.env.user)

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # archive groups - Default Group By 'create_date'
        archive_groups = False
        
        domain = [('employee_id','=',request.env.user.employee_id.id)]

        # pager

        payslip_count = HrPayslips.sudo().search_count(domain)
        
        pager = request.website.pager(
            url="/my/payslips/list",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=payslip_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        payslip_ids = HrPayslips.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'date': date_begin,
            'payslip_ids': payslip_ids,
            'page_name': 'Payslips',
            'archive_groups': archive_groups,
            'default_url': '/my/payslips/list',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'payslip_count':payslip_count
            
        })
        return request.render("nl_payroll.portal_my_payslips", values)

    

    @http.route('/my/payslip/download', type='http', auth="user", website=True)
    def download_payslip_pdf(self, **kw):
        redirect = kw.get('redirect')
        print(redirect)
        payslip_id = request.env['hr.payslip'].sudo().search([('id','=',kw.get('id'))])
        report_template_id = http.request.env.ref(
            'hr_payroll.action_report_payslip').sudo()._render_qweb_pdf(payslip_id.id)
        
        data_record = base64.b64encode(report_template_id[0])
        payslip_id.pdf_result = data_record
        if redirect == 'self':
            return request.redirect('/my/payroll/view/payslip?id='+str(payslip_id.id))
        else:
            return request.redirect('/my/payslips/list')


    @http.route('/my/payroll/view/payslip', type="http", auth="user", website=True)
    def view_employee_payslip(self, **kw):
        id = kw.get('id')
        if id:
            payslip = request.env['hr.payslip'].sudo().search([('id','=',id),('employee_id','=',request.env.user.employee_id.id)])
            if payslip:
                return request.render('nl_payroll.portal_my_payslip', {
                    'payslip':payslip
                })
            else:
                return request.render('http_routing.404')
        else:
            return request.render('http_routing.404')

    