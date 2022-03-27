import datetime

from odoo import fields
from odoo import http
from odoo.http import request,content_disposition
from odoo.addons.portal.controllers.portal import CustomerPortal

from datetime import datetime, time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, DEFAULT_SERVER_DATETIME_FORMAT as DTF

from odoo.tools.translate import _

from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from collections import OrderedDict
import base64
import json
from datetime import timedelta

class WebsiteAccount(CustomerPortal):
    
    @http.route(['/my/leave/approve/approve'], type='http', auth="user", website=True)
    def approve_leave_from_portal_employee(self, **kw):
        id = request.params.get('id')
        leave_id = request.env['hr.leave'].sudo().search([('id','=',id)])
        if leave_id.employee_id.leave_manager_id.id == request.env.user.id:
            leave_id.action_approve()
            return http.request.redirect('/my/leaves/approve/')

    @http.route(['/my/leave/approve/deny'], type='http', auth="user", website=True)
    def refuse_leave_from_portal(self, **kw):
        id = request.params.get('id')
        leave_id = request.env['hr.leave'].sudo().search([('id','=',id)])
        if leave_id.employee_id.leave_manager_id.id == request.env.user.id:
            leave_id.action_refuse()
            return http.request.redirect('/my/leaves/approve/')

    def get_domain_my_leaves_approve(self, user):
        # user => logged in user
        emp = request.env['hr.employee'].sudo().search([('leave_manager_id', '=', user.id)])

        employee_ids = []
        for item in emp:
            employee_ids.append(item.id)

        return [
            ('employee_id', 'in', employee_ids),
        ]

    
    @http.route(['/my/allocation/approve/approve'], type='http', auth="user", website=True)
    def approve_allocation_from_portal_employee(self, **kw):
        id = request.params.get('id')
        allocation_id = request.env['hr.leave.allocation'].sudo().search([('id','=',id)])
        if allocation_id.employee_id.leave_manager_id.id == request.env.user.id:
            allocation_id.action_approve()
            return http.request.redirect('/my/allocation/approve/')


    @http.route(['/my/allocation/approve/deny'], type='http', auth="user", website=True)
    def refuse_allocation_from_portal(self, **kw):
        id = request.params.get('id')
        allocation_id = request.env['hr.leave.allocation'].sudo().search([('id','=',id)])
        if allocation_id.employee_id.leave_manager_id.id == request.env.user.id:
            allocation_id.action_refuse()
            return http.request.redirect('/my/allocation/approve/')


    @http.route(['/my/allocation/approve', '/my/allocation/approve/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_allocation_approve(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='all', **kw):
        values = self._prepare_portal_layout_values()
        LeaveAllocation = request.env['hr.leave.allocation']
        domain = self.get_domain_my_leaves_approve(request.env.user)
        domain += [('state', 'in', ['confirm', 'validate1'])]
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'start_date': {'label': _('Start Date'), 'order': 'date_from desc'},
            'end_date': {'label': _('End Date'), 'order': 'date_to desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'Confirmed': {'label': _('To Approve'), 'domain': [('state', '=', 'confirm')]},
            'Validated': {'label': _('To Validate'), 'domain': [('state', '=', 'validate1')]},
            'Refused': {'label': _('To Refuse'), 'domain': [('state', '=', 'refuse')]},
            'Cancelled': {'label': _('Cancelled'), 'domain': [('state', '=', 'cancel')]},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # archive groups - Default Group By 'create_date'
        # archive_groups = self._get_archive_groups('hr.leave.allocation', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        
        allocation_count = LeaveAllocation.search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/allocation/approve",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=allocation_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        allocations = LeaveAllocation.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_allocations_history'] = allocations.ids[:100]
        values.update({
            'date': date_begin,
            'allocations': allocations,
            'page_name': 'leave_allocation_approve',
            'default_url': '/my/allocation/approve',
            'pager': pager,
            
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': '/my/allocation/approve',
        })
        return request.render("nl_leave_portal.portal_my_allocation_details_approve", values)
    

    @http.route(['/my/leaves/approve', '/my/leaves/approve/page/<int:page>'], type='http', auth="user", website=True)
    def approve_leave_from_portal(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        HrLeave = request.env['hr.leave']
        domain = self.get_domain_my_leaves_approve(request.env.user)
        domain += [('state', 'in', ['confirm', 'validate1'])]

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
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # pager

        leave_count = HrLeave.sudo().search_count(domain)
        pager = request.website.pager(
            url="/my/leaves/approve",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=leave_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        leaves = HrLeave.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        attachments = {}
        for leave in leaves:
            attachments[leave.id] = {"leave_id": leave.id, "has_attachment": False}
            request._cr.execute("""
                SELECT count(id) FROM ir_attachment WHERE res_model  = 'hr.leave' AND res_id = %s LIMIT 1
                """, (leave.id,))
            if request._cr.dictfetchone().get('count', 0):
                attachments[leave.id].update({'has_attachment': True})
        values.update({
            'date': date_begin,
            'leaves': leaves,
            'page_name': 'leave',
            'archive_groups': archive_groups,
            'default_url': '/my/leaves/approve',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'attachments': attachments,
        })
        return request.render("nl_leave_portal.portal_my_leaves_details_approve", values)
    
    MANDATORY_BILLING_FIELDS = ["description","from_date","leave_type"]
    MANDATORY_SUBORDINATES_FIELDS = ["description", "from_date", "leave_type", "employee_id"]
    MANDATORY_FIELDS_DESCRIPTION = {"description": "Description", "from_date": "From Date", "leave_type": "Leave Type", "employee_id": "Employee"}

    def get_domain_my_leaves(self, user):
        # user => logged in user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        return [
            ('employee_id', '=', emp and emp.id or False),
        ]

    def _prepare_portal_layout_values(self):
        values = super(WebsiteAccount, self)._prepare_portal_layout_values()
        leave_count_approve = request.env['hr.leave'].sudo().search_count([('employee_id.leave_manager_id','=',request.env.user.id), ('state', 'in', ['confirm', 'validate1'])])
        allocation_request_count = request.env['hr.leave.allocation'].sudo().search_count([('employee_id.user_id','=',request.env.user.id)])
        allocatoin_request_approve_count = request.env['hr.leave.allocation'].sudo().search_count([('employee_id.leave_manager_id','=',request.env.user.id), ('state', 'in', ['confirm', 'validate1'])])
        show = False
        show_allocation = False
        if leave_count_approve > 0:
            show = True
        if allocatoin_request_approve_count > 0:
            show_allocation = True
        leave_count = request.env['hr.leave'].search_count(self.get_domain_my_leaves(request.env.user))

        show_create_subordinates = False
        subordinates_leave_count = 0
        if request.env.user.employee_id:
            sub_emp_ids = self.get_current_user_subordinates_employees().mapped('id')
            subordinates_leave_count = request.env['hr.leave'].sudo().search_count([('employee_id', 'in', sub_emp_ids), ('state', 'in', ['confirm'])])
            if len(sub_emp_ids) > 0 and request.env.user.employee_id:
                show_create_subordinates = True

        values.update({
            'leave_count': leave_count,
            'leave_count_approve':leave_count_approve,
            'show':show,
            'show_allocation':show_allocation,
            'allocatoin_request_approve_count':allocatoin_request_approve_count,
            'allocation_request_count':allocation_request_count,
            'subordinates_leave_count':subordinates_leave_count,
            'show_create_subordinates': show_create_subordinates
        })
        return values

    def details_form_validate_leave_request(self, data, for_subordinates=False):
        user = request.env.user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        error = dict()
        error_message = []

        # Validation
        to_loop_fields = self.MANDATORY_BILLING_FIELDS
        if for_subordinates:
            to_loop_fields = self.MANDATORY_SUBORDINATES_FIELDS

        for field_name in to_loop_fields:
            if not data.get(field_name):
                error[self.MANDATORY_FIELDS_DESCRIPTION.get(field_name)] = 'missing'

        # if not 'request_unit_half' in data and (not 'to_date' in data or data.get('to_date', False) in ['To', '']):
        #     error['End Date or half day'] = 'missing'

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('The following fields are missing'))

        # Validation for same date request
        if data.get('request_date_from') and data.get('request_date_to'):
            h_status_id = int(data.get('holiday_status_id'))
            h_s_id = request.env['hr.leave.type'].sudo().browse(h_status_id or False)
            dt_from = data.get('request_date_from')
            dt_to = data.get('request_date_to')
            if dt_from:
                dt_from = datetime.strptime(dt_from, DF).date()
            if dt_to != "To":
                dt_to = datetime.strptime(dt_to, DF).date()
            if dt_to == 'To':
                dt_to = dt_from
            domain = [
                    ('date_from', '<=', dt_to),
                    ('date_to', '>=', dt_from),
                    ('employee_id', '=', emp and emp.id or False),
                    ('state', 'not in', ['cancel', 'refuse']),
            ]
            nholidays = request.env['hr.leave'].search_count(domain)
            if nholidays:
                error.update({'overlap': True})
                error_message.append(_('You can not set 2 time off that overlaps on the same day for the same employee.'))

            # Validation for leave type validity check
            vstart = h_s_id.validity_start
            vstop = h_s_id.validity_stop
            if h_s_id.validity_start and h_s_id.validity_stop:
                if dt_from and dt_to and (dt_from < vstart or dt_to > vstop):
                    error.update({'valid_between': True})
                    error_message.append(_('%s are only valid between %s and %s') % (
                            h_s_id.display_name, h_s_id.validity_start, h_s_id.validity_stop))
            elif h_s_id.validity_start:
                if dt_from and (dt_from < vstart):
                    error.update({'valid_start': True})
                    error_message.append(_('%s are only valid starting from %s') % (
                        h_s_id.display_name, h_s_id.validity_start))
            elif h_s_id.validity_stop:
                if dt_to and (dt_to > vstop):
                    error.update({'valid_stop': True})
                    error_message.append(_('%s are only valid until %s') % (
                        h_s_id.display_name, h_s_id.validity_stop))

            # Check Allocation of employee
            leave_days = h_s_id.get_days(emp and emp.id or False)[h_s_id.id]
            if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                error.update({'sufficient_timeoff': True})
                error_message.append(_('The number of remaining time off is not sufficient for this time off type.\n'
                                        'Please also check the time off waiting for validation.'))

        return error, error_message


    def get_domain_my_allocations(self, user):
        # user => logged in user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        return [
            ('employee_id', '=', emp and emp.id or False),
        ]

    @http.route(['/my/allocations', '/my/allocations/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_allocations(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='all', **kw):
        values = self._prepare_portal_layout_values()
        LeaveAllocation = request.env['hr.leave.allocation']
        domain = self.get_domain_my_allocations(request.env.user)

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'start_date': {'label': _('Start Date'), 'order': 'date_from desc'},
            'end_date': {'label': _('End Date'), 'order': 'date_to desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'Confirmed': {'label': _('To Approve'), 'domain': [('state', '=', 'confirm')]},
            'Validated': {'label': _('To Validate'), 'domain': [('state', '=', 'validate1')]},
            'Refused': {'label': _('To Refuse'), 'domain': [('state', '=', 'refuse')]},
            'Cancelled': {'label': _('Cancelled'), 'domain': [('state', '=', 'cancel')]},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # archive groups - Default Group By 'create_date'
        # archive_groups = self._get_archive_groups('hr.leave.allocation', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        
        allocation_count = LeaveAllocation.search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/allocations",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=allocation_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        allocations = LeaveAllocation.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_allocations_history'] = allocations.ids[:100]
        values.update({
            'date': date_begin,
            'allocations': allocations,
            'page_name': 'leave_allocation',
            'default_url': '/my/allocations',
            'pager': pager,
            
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': '/my/allocations',
        })
        return request.render("nl_leave_portal.portal_my_allocations", values)

    def get_days_all_request_allocation(self):
        leave_types = sorted(request.env['hr.leave.type'].sudo().search([('allocation_type','=','fixed_allocation')]).filtered(lambda x: x.virtual_remaining_leaves or x.max_leaves), key=self._model_sorting_key, reverse=True)
        return [(lt.name, {
                    'remaining_leaves': ('%.2f' % lt.remaining_leaves).rstrip('0').rstrip('.'),
                    'virtual_remaining_leaves': ('%.2f' % lt.virtual_remaining_leaves).rstrip('0').rstrip('.'),
                    'max_leaves': ('%.2f' % lt.max_leaves).rstrip('0').rstrip('.'),
                    'leaves_taken': ('%.2f' % lt.leaves_taken).rstrip('0').rstrip('.'),
                    'virtual_leaves_taken': ('%.2f' % lt.virtual_leaves_taken).rstrip('0').rstrip('.'),
                    'request_unit': lt.request_unit,
                    'expires_on':lt.validity_stop,
                    'id':lt.id,
                }, lt.allocation_type, lt.validity_stop)
            for lt in leave_types]

    @http.route(['/my/allocation/create'], type='http', auth="user", website=True)
    def create_allocation(self, **kw):

        holiday_type_ids = request.env['hr.leave.type'].search([('allocation_type','=','fixed_allocation')])
        user = request.env.user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                              limit=1)
        
        timeoffs = self.get_days_all_request_allocation()
        values = {
            
            'holiday_type_ids':holiday_type_ids,
            'emp':emp,
            'timeoffs':timeoffs

            }
        return request.render("nl_leave_portal.my_allocation_create", values)
        

    @http.route(['/my/leaves', '/my/leaves/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_leaves(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        HrLeave = request.env['hr.leave']
        domain = self.get_domain_my_leaves(request.env.user)

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
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # pager
        leave_count = HrLeave.search_count(domain)
        pager = request.website.pager(
            url="/my/leaves",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=leave_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        leaves = HrLeave.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'date': date_begin,
            'leaves': leaves,
            'page_name': 'leave',
            'archive_groups': archive_groups,
            'default_url': '/my/leaves',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("nl_leave_portal.portal_my_leaves_details", values)


    @http.route(['/my/leave/create'], type='http', auth="user", website=True)
    def create_leave(self, **kw):
        timeoffs = self.get_days_all_request()
        values = {'timeoffs':timeoffs}
        return request.render("nl_leave_portal.my_leave_create", values)

    # get hr_leave date_from.
    def get_leave_date_from(self):
        leaves = request.env['hr.leave'].search([('employee_id', '=', request.env.user.employee_ids.id)])
        leave_dates = {}
        #pull all leave dates in leave_dates dict.
        for leave in leaves:
            leave_dates['date_from'] = leave.date_from.strftime('%Y-%m-%d')
        return leave_dates

    
    def _model_sorting_key(self, leave_type):
        remaining = leave_type.virtual_remaining_leaves > 0
        taken = leave_type.leaves_taken > 0
        return leave_type.allocation_type == 'fixed' and remaining, leave_type.allocation_type == 'fixed_allocation' and remaining, taken

    def get_days_all_request(self, employee_id=False):
        if employee_id:
            leave_types = sorted(request.env['hr.leave.type'].sudo().with_context(employee_id=employee_id).search([]).filtered(lambda x: x.virtual_remaining_leaves or x.max_leaves), key=self._model_sorting_key, reverse=True)
        else: 
            leave_types = sorted(request.env['hr.leave.type'].sudo().search([]).filtered(lambda x: x.virtual_remaining_leaves or x.max_leaves), key=self._model_sorting_key, reverse=True)
        return [(lt.name, {
                    'remaining_leaves': ('%.2f' % lt.remaining_leaves).rstrip('0').rstrip('.'),
                    'virtual_remaining_leaves': ('%.2f' % lt.virtual_remaining_leaves).rstrip('0').rstrip('.'),
                    'max_leaves': ('%.2f' % lt.max_leaves).rstrip('0').rstrip('.'),
                    'leaves_taken': ('%.2f' % lt.leaves_taken).rstrip('0').rstrip('.'),
                    'virtual_leaves_taken': ('%.2f' % lt.virtual_leaves_taken).rstrip('0').rstrip('.'),
                    'request_unit': lt.request_unit,
                    'expires_on':lt.validity_stop,
                    'id':lt.id,
                    'require_attachments':lt.require_attachments,
                    'require_attachments_after_days':lt.require_attachments_after_days
                }, lt.allocation_type, lt.validity_stop)
            for lt in leave_types]

    def get_total_allocation_employee_current_year(self):
            """
            get total allocation of employee current year
            """
            emp = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)],
                                                    limit=1)
            if emp:
                year = datetime.now().year
                allocation = request.env['hr.leave.allocation'].search([('employee_id', '=', emp.id),
                                                                         ('date_from', 'like', '%' + str(year) + '%')])
                if allocation:
                    return allocation
                else:
                    return 0
            else:   
                return 0


    @http.route(['/my/allocation/submit'], type='http', auth="user", website=True)
    def submit_allocation(self,redirect=None, **kw):
        """
        Submit leave allocatoin request
        """
        values = {}
        for field_name, field_value in kw.items():
            values[field_name] = field_value
        if values:
            hs_id = request.env['hr.leave.type'].sudo().browse(int(kw.get('leave_type', False)))
            values['employee_id'] = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)],limit=1).id
            values['name'] = 'Allocation Request From ' + request.env.user.employee_id.name + ' For ' + hs_id.name
            values['number_of_days'] = int((values['number_of_days']))
            values['holiday_status_id'] = hs_id and hs_id.id,
            values['number_of_days_display'] = (values['number_of_days'])
            values['notes'] = values['description']

            allocation_id = request.env['hr.leave.allocation'].sudo().create({
                'employee_id': values['employee_id'],
                'name': values['name'].strip(),
                'notes': values['description'].strip(),
                'holiday_status_id': values['holiday_status_id'],
                'number_of_days': values['number_of_days'],
                'number_of_days_display': values['number_of_days_display'],

            })
            if allocation_id:
                return request.redirect('/my/allocations/')
           
        
        

    @http.route(['/my/leave/submit'], type='http', auth="user", method=['POST'], website=True)
    def submit_leave(self, redirect=None, **post):

        values ={}
        error, error_message = self.details_form_validate_leave_request(post)
        values.update({'error': error, 'error_message': error_message})
        user = request.env.user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        dt_from = post.get('from_date')
        dt_to = post.get('to_date')
        old_data = {
            'half_day': True if 'request_unit_half' in post and post.get("request_unit_half") == 'on' else False, 
            'from_date': post.get('from_date') if post.get('from_date') else '', 
            'to_date': post.get('to_date') if post.get('to_date') != 'To' else '', 
            'description': post.get('description'), 
            "leave_type_id": post.get('leave_type', False),
            }
        if not error:
            leave_type_id = int(post.get('leave_type'))
            dt_from = post.get('from_date')
            dt_to = post.get('to_date')
            if not dt_to:
                dt_to = 'To'
            values.update(post)
            if dt_from:
                dt_from = datetime.strptime(dt_from, DF)
            if dt_to =='To':
                dt_to = dt_from
            else:
                dt_to = datetime.strptime(dt_to, DF)

            if 'request_unit_half' in post and post.get("request_unit_half") == 'on':
                values = {
                    'holiday_status_id': leave_type_id,
                    'name': post.get('description'),
                    'request_date_from':dt_from.strftime('%Y-%m-%d'),
                    'request_date_to': dt_to.strftime('%Y-%m-%d'),
                    'employee_id' : emp and emp.id or False,
                    'user_id': user and user.id or False,
                    'request_date_from_period':'am',
                    'request_unit_half':True
                    }
            else:
                values = {
                    'holiday_status_id': leave_type_id,
                    'name': post.get('description'),
                    'request_date_from':dt_from.strftime('%Y-%m-%d'),
                    'request_date_to': dt_to.strftime('%Y-%m-%d'),
                    'employee_id' : emp and emp.id or False,
                    'user_id': user and user.id or False,
                    }

            if 'request_unit_half' in post and post.get("request_unit_half") == 'on':
                values.update({
                    'request_unit_half': True,
                    'request_date_from_period': 'am',
                    })
            if 'request_unit_hours' in post and post.get("request_unit_hours") == 'on':
                values.update({
                    'request_unit_hours' : True,
                    'request_hour_from': post.get('request_hour_from'),
                    'request_hour_to': post.get('request_hour_to'),
                    })
            try:
                tmp_leave = request.env['hr.leave'].sudo().new(values)
                tmp_leave._onchange_request_parameters()
                tmp_leave._compute_date_from_to()
                values  = tmp_leave._convert_to_write(tmp_leave._cache)
                new_leave = request.env['hr.leave'].sudo().create(values)
                if new_leave and post.get('attachment', False):
                    attachment = post.get('attachment')
                    Attachments = request.env['ir.attachment']
                    attachment_id = Attachments.sudo().create({
                    'name': "leave_attachment",
                    'res_name': attachment.filename,
                    'res_model': 'hr.leave',
                    'res_id': new_leave.id, 
                    'res_id': new_leave.id,  
                    'datas': base64.encodestring(attachment.read())
                    })
                    new_leave.leave_attachment = attachment_id.datas
            except Exception as e:
                request._cr.rollback()
                values = {
                    'name': post.get('description', ''),
                    'redirect': redirect,
                    'message':str(e),
                    'errors': str(e),
                    'old_data': old_data,
                    'error_type': 'other',
                    'timeoffs': self.get_days_all_request(),
                    }
                response = request.render("nl_leave_portal.my_leave_create", values)
                response.headers['X-Frame-Options'] = 'DENY'
                return response
            if redirect:
                return request.redirect(redirect)
            return request.redirect('/my/leaves')
        values.update({
            'name': post.get('description', ''),
            'redirect': redirect,
            'message':values.get('error_message'),
            'errors':values.get('error'),
            'old_data': old_data,
            'error_type': "validations",
            'timeoffs': self.get_days_all_request(),
            })
        response = request.render("nl_leave_portal.my_leave_create", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route(['/my/leave/approve/attachment'], type='http', auth="user", website=True)
    def download_leave_attachment_from_portal(self, **post):
        leave_id = request.env['hr.leave'].sudo().browse(int(post.get('id', False)))
        if leave_id:
            request._cr.execute("""
                SELECT id FROM ir_attachment WHERE res_model  = 'hr.leave' AND res_id = %s LIMIT 1
            """, (leave_id.id,))
            record = request._cr.dictfetchone()
            if record:
                attachment = request.env['ir.attachment'].sudo().search([('id', '=', record.get('id'))])
                if attachment:
                    return request.make_response(base64.decodestring(attachment.datas),
                                                [('Content-Type', 'application/octet-stream'),
                                                ('Content-Disposition', 'attachment; filename=' + attachment.name)])
        
        
    @http.route(['/employee/leave/dates'], type='http', auth="user", website=True)
    def get_employee_leave_dates(self, **post):
        vals = {}
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        leave_ids = request.env['hr.leave'].sudo().search([('employee_id', '=', emp.id)])
        disabledDates = []
        for leave in leave_ids:
            if leave.date_from and leave.date_to:
                dates = self.get_dates(leave.request_date_from, leave.request_date_to)
                disabledDates = disabledDates + dates
        vals.update({  
            'disabledDates': disabledDates,
        })
        return json.dumps(vals, indent=2, sort_keys=True, default=str)
    


    #function to reuturn dates betweeen two dates.
    def get_dates(self, start_date, end_date):
        dates = []
        for n in range(int((end_date - start_date).days + 1)):
            dates.append(start_date + timedelta(n))
        return dates

    # Subordinators leave part
    @http.route(['/my/subordinates/leaves', '/my/subordinates/leaves/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_subordinates_leaves(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        """ This function return subordinates leave list view """
        values = self._prepare_portal_layout_values()
        HrLeave = request.env['hr.leave']

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
        leave_count = HrLeave.search_count(domain)
        pager = request.website.pager(
            url="/my/subordinates/leaves",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=leave_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        leaves = HrLeave.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        show_create_subordinates = False
        if len(self.get_current_user_subordinates_employees().mapped('id')) > 0:
            show_create_subordinates = True

        values.update({
            'date': date_begin,
            'leaves': leaves,
            'page_name': 'Subordinates leave',
            # 'archive_groups': archive_groups,
            'default_url': '/my/subordinates/leaves',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'show_create_subordinates': show_create_subordinates
        })
        return request.render("nl_leave_portal.portal_my_subordinates_leaves_details", values)

    @http.route(['/subordinates/leave/create'], type='http', auth="user", website=True)
    def create_subordinates_leave(self, **kw):
        """ This function return subordinates leave form view. """

        subordinates_employees = self.get_current_user_subordinates_employees()
        values = {'subordinates_employees': subordinates_employees}
        return request.render("nl_leave_portal.subordinates_leave_create", values)
    
    @http.route(['/get_employee_leave'], type='http', auth="user", method=['POST'], website=True)
    def get_employee_leave_ajax(self, **kw):
        """This function get timoffs data for an employee and return json data."""
        timeoffs = self.get_days_all_request(employee_id=int(kw['employee_id']))
        return json.dumps(timeoffs, indent=4, sort_keys=True, default=str)


    @http.route(['/subordinates/leave/submit'], type='http', auth="user", method=["POST"] ,website=True)
    def submit_subordinates_leave(self, redirect=None, **post):
        """ This function handle submited form data of subordinators leave request """
        values ={}
        error, error_message = self.details_form_validate_leave_request(post, for_subordinates=True)
        values.update({'error': error, 'error_message': error_message})
        old_data = {
            'employee_id': post.get('employee_id', False), 
            'half_day': True if 'request_unit_half' in post and post.get("request_unit_half") == 'on' else False, 
            'from_date': post.get('from_date') if post.get('from_date') else '', 
            'to_date': post.get('to_date') if post.get('to_date') != 'To' else '', 
            'description': post.get('description'), 
            "leave_type_id": post.get('leave_type', False),
            }
        if not error:
            leave_type_id = int(post.get('leave_type', False))
            employee_id = int(post.get('employee_id', False))
            user = request.env['hr.employee'].browse(employee_id).user_id
        
            dt_from = post.get('from_date')
            dt_to = post.get('to_date')
            if not dt_to:
                dt_to = 'To'
            values.update(post)
            if not error:
                if dt_from:
                    dt_from = datetime.strptime(dt_from, DF)
                if dt_to =='To':
                    dt_to = dt_from
                else:
                    dt_to = datetime.strptime(dt_to, DF)
                
                if 'request_unit_half' in post and post.get("request_unit_half") == 'on':
                    values = {
                        'holiday_status_id':leave_type_id,
                        'name': post.get('description'),
                        'request_date_from':dt_from.strftime('%Y-%m-%d'),
                        'request_date_to': dt_to.strftime('%Y-%m-%d'),
                        'employee_id' : employee_id,
                        'user_id': user and user.id or False,
                        'request_date_from_period':'am',
                        'request_unit_half':True
                        }
                else:
                    values = {
                        'holiday_status_id':leave_type_id,
                        'name': post.get('description'),
                        'request_date_from':dt_from.strftime('%Y-%m-%d'),
                        'request_date_to': dt_to.strftime('%Y-%m-%d'),
                        'employee_id' : employee_id,
                        'user_id': user and user.id or False,
                        }

                if 'request_unit_half' in post and post.get("request_unit_half") == 'on':
                    values.update({
                        'request_unit_half': True,
                        'request_date_from_period': 'am',
                        'number_of_days': 0.5
                        })
                if 'request_unit_hours' in post and post.get("request_unit_hours") == 'on':
                    values.update({
                        'request_unit_hours' : True,
                        'request_hour_from': post.get('request_hour_from'),
                        'request_hour_to': post.get('request_hour_to'),
                        })
                try:
                    tmp_leave = request.env['hr.leave'].sudo().new(values)
                    tmp_leave._onchange_request_parameters()
                    tmp_leave._compute_date_from_to()
                    values  = tmp_leave._convert_to_write(tmp_leave._cache)
                    new_leave = request.env['hr.leave'].sudo().create(values)
                    if self.is_current_user_manager(new_leave.employee_id):
                        new_leave.action_approve()
                    if new_leave.state != 'validate' and self.is_current_user_manager(new_leave.employee_id):
                        new_leave.action_validate()

                    if new_leave and post.get('attachment', False):
                        attachment = post.get('attachment')
                        Attachments = request.env['ir.attachment']
                        attachment_id = Attachments.sudo().create({
                        'name': "leave_attachment",
                        'res_name': attachment.filename,
                        'res_model': 'hr.leave',
                        'res_id': new_leave.id,  
                        'type': 'binary',
                        'datas': base64.encodestring(attachment.read())
                        })
                        new_leave.leave_attachment = attachment_id.datas
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
                    response = request.render("nl_leave_portal.subordinates_leave_create", values)
                    response.headers['X-Frame-Options'] = 'DENY'
                    return response
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/subordinates/leaves')

        values.update({
            'name': post.get('description', ''),
            'redirect': redirect,
            'old_data': old_data,
            'message':values.get('error_message'),
            'errors':values.get('error'),
            'error_type': "validations",
            'subordinates_employees': self.get_current_user_subordinates_employees()
            })
        response = request.render("nl_leave_portal.subordinates_leave_create", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


    def get_current_user_subordinates_employees(self):
        current_user_employee = request.env.user.employee_id
        all_parents_ids = []
        if current_user_employee:
            all_parents_ids.append(current_user_employee.id)
            substitute_approvers  = request.env['hr.employee'].sudo().search([('leave_responsible_substitue', '=', current_user_employee.id)]).mapped('id')
            all_parents_ids = all_parents_ids + substitute_approvers
        return request.env['hr.employee'].sudo().search([('parent_id', 'in', all_parents_ids), (('id', '!=', current_user_employee.id))])

    def is_current_user_manager(self, employee):
        if request.env.user.employee_id and employee.parent_id == request.env.user.employee_id:
            return True
        return False

