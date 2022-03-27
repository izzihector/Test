from odoo import fields
from odoo import http
from odoo.http import request,content_disposition
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import ValidationError
from datetime import datetime, time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, DEFAULT_SERVER_DATETIME_FORMAT as DTF

from odoo.tools.translate import _

from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from collections import OrderedDict
import base64
import json
from datetime import timedelta


class WebsiteAppraisalPIP(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(WebsiteAppraisalPIP, self)._prepare_portal_layout_values()
        show_subordinates_allocations = False
        subordinates_allocations_count = 0

        if request.env.user.employee_id:
            sub_emp_ids = self.get_current_user_subordinates_employees().mapped('id')
            subordinates_allocations_count = request.env['hr.leave.allocation'].sudo().search_count([('employee_id', 'in', sub_emp_ids), ('state', 'in', ['confirm'])])
            if len(sub_emp_ids) > 0 and request.env.user.employee_id:
                show_subordinates_allocations = True

        values.update({
            'show_subordinates_allocations': show_subordinates_allocations,
            'subordinates_allocations_count': subordinates_allocations_count
            })

        return values

    # Subordinators leave part
    @http.route(['/my/subordinates/allocations', '/my/subordinates/allocations/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_subordinates_allocations(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        """ This function return subordinates allocations list view """
        values = self._prepare_portal_layout_values()
        HrAllocation = request.env['hr.leave.allocation']

        employee_ids = self.get_current_user_subordinates_employees().mapped('id')
        
        domain = [('employee_id', 'in', employee_ids)]
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['confirm', 'validate1', 'validate'])]},
            'confirm': {'label': _('To Approve'), 'domain': [('state', '=', 'confirm')]},
            'second_approval': {'label': _('Second Approval'), 'domain': [('state', '=', 'validate1')]},
            'validated': {'label': _('Approved'), 'domain': [('state', '=', 'validate')]}
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        if not filterby:
            filterby = 'confirm'
        domain += searchbar_filters[filterby]['domain']

        # archive groups - Default Group By 'create_date'
        # archive_groups = False
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # pager
        allocations_count = HrAllocation.search_count(domain)
        pager = request.website.pager(
            url="/my/subordinates/allocations",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=allocations_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        allocations = HrAllocation.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        show_subordinates_allocations = False
        if len(self.get_current_user_subordinates_employees().mapped('id')) > 0:
            show_subordinates_allocations = True

        values.update({
            'date': date_begin,
            'allocations': allocations,
            'page_name': 'Subordinates leave',
            # 'archive_groups': archive_groups,
            'default_url': '/my/subordinates/allocations',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'show_subordinates_allocations': show_subordinates_allocations
        })
        return request.render("nl_leave_portal.portal_my_subordinates_allocations_details", values)


    @http.route(['/subordinates/allocations/create'], type='http', auth="user", website=True)
    def create_subordinates_allocations(self, **kw):
        """ This function return subordinates leave form view. """
        values = {}
        subordinates_employees = self.get_current_user_subordinates_employees()
        values.update({'subordinates_employees': subordinates_employees})
        return request.render("nl_leave_portal.subordinates_allocation_create", values)

    @http.route(['/get_employee_allocation'], type='http', auth="user", method=['POST'], website=True)
    def get_employee_allocation_ajax(self, **kw):
        """This function get timoffs data for an employee and return json data."""
        employee_id = kw.get('employee_id', False)
        if employee_id:
            timeoffs = request.env['hr.leave.type'].sudo().with_context(employee_id=int(employee_id)).search([('allocation_type','=','fixed_allocation')])
        else:
            timeoffs = request.env['hr.leave.type'].sudo().search([('allocation_type','=','fixed_allocation')])
        data = [(lt.name, {
                    'remaining_leaves': ('%.2f' % lt.remaining_leaves).rstrip('0').rstrip('.'),
                    'virtual_remaining_leaves': ('%.2f' % lt.virtual_remaining_leaves).rstrip('0').rstrip('.'),
                    'max_leaves': ('%.2f' % lt.max_leaves).rstrip('0').rstrip('.'),
                    'leaves_taken': ('%.2f' % lt.leaves_taken).rstrip('0').rstrip('.'),
                    'virtual_leaves_taken': ('%.2f' % lt.virtual_leaves_taken).rstrip('0').rstrip('.'),
                    'id':lt.id,
                }, lt.allocation_type, lt.validity_stop)
            for lt in timeoffs]
        return json.dumps(data, indent=4, sort_keys=True, default=str)


    
    @http.route(['/subordinates/allocations/submit'], type='http', auth="user", website=True)
    def submit_subordinates_allocation(self, redirect=None, **post):
        """
        Submit subordinates leave allocatoin request
        """
        values = {}
        error = {}
        error_message = ''
        old_data = post
        all_fields = {'employee_id': 'Employeee', 'leave_type': 'Leave Type', 'number_of_days': 'Number of Days', 'description': 'Description'}
        for field_name, val in all_fields.items():
            if not post.get(field_name, False):
                error[val] = 'missing'
        if error:
            error_message = 'The following fields are missing.'

        if not error:
            for field_name, field_value in post.items():
                values[field_name] = field_value
            if values:
                try:
                    hs_id = request.env['hr.leave.type'].sudo().browse(int(post.get('leave_type', False)))
                    values['employee_id'] = int(post.get('employee_id', False))
                    values['name'] = 'Allocation Request From ' + request.env.user.employee_id.name + ' For ' + hs_id.name
                    values['number_of_days'] = int((values['number_of_days']))
                    values['holiday_status_id'] = hs_id and hs_id.id,
                    values['number_of_days_display'] = (values['number_of_days'])
                    values['notes'] = values['description']
                    new_allocation = request.env['hr.leave.allocation'].sudo().create({
                        'employee_id': values['employee_id'],
                        'name': values['name'].strip(),
                        'notes': values['description'].strip(),
                        'holiday_status_id': values['holiday_status_id'],
                        'number_of_days': values['number_of_days'],
                        'number_of_days_display': values['number_of_days_display'],
                        'allocation_type': 'regular',
                        'holiday_type': 'employee'
                        })
                    if self.is_current_user_manager(new_allocation.employee_id):
                        new_allocation.action_approve()
                    if new_allocation.state != 'validate' and self.is_current_user_manager(new_allocation.employee_id):
                        new_allocation.action_validate()
                    
                except Exception as e:
                    request._cr.rollback()
                    values = {
                        'name': post.get('description', ''),
                        'redirect': redirect,
                        'message':str(e),
                        'errors': str(e),
                        'old_data': old_data,
                        'error_type': 'other',
                        'subordinates_employees': self.get_current_user_subordinates_employees()
                        }
                    response = request.render("nl_leave_portal.subordinates_allocation_create", values)
                    response.headers['X-Frame-Options'] = 'DENY'
                    return response

                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/subordinates/allocations')

                # allocation_id = request.env['hr.leave.allocation'].sudo().create({
                #     'employee_id': values['employee_id'],
                #     'name': values['name'].strip(),
                #     'notes': values['description'].strip(),
                #     'holiday_status_id': values['holiday_status_id'],
                #     'number_of_days': values['number_of_days'],
                #     'number_of_days_display': values['number_of_days_display'],

                # })
                # if allocation_id:
                #     return request.redirect('/my/allocations/')
        

        values.update({
            'name': post.get('description', ''),
            'redirect': redirect,
            'old_data': old_data,
            'message': error_message,
            'errors': error,
            'error_type': "validations",
            'subordinates_employees': self.get_current_user_subordinates_employees()
            })
        # request.params['values'] = values
        # return request.redirect('/subordinates/allocations/create?error=validation')
        response = request.render("nl_leave_portal.subordinates_allocation_create", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response