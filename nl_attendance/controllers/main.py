import datetime

from odoo import http, _, fields
from odoo.http import request
from odoo.addons.hr_attendance.controllers.main import HrAttendance
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.osv.expression import AND
from werkzeug.exceptions import NotFound
from operator import itemgetter
from odoo.tools import groupby as groupbyelem
from collections import OrderedDict
import calendar


class WebsiteAccountExtended(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(WebsiteAccountExtended, self)._prepare_portal_layout_values()
        show_my_attendance = False if not request.env.user.employee_id else True
        values.update({
            'show_my_attendance': show_my_attendance
            })
        return values

class HrAttendanceExtended(HrAttendance):
    _items_per_page = 20
    @http.route(['/my/attendance', '/my/attendance/page/<int:page>'], auth='user', type='http', website=True)
    def my_attendance(self, page=1, date_begin=None, filterby=None ,date_end=None, sortby=None, search=None, search_in='all', groupby='none', **kw):
        employee = request.env.user.employee_id
        values = {}
        attendance_obj = request.env['hr.attendance'].sudo()
        if not employee:
            raise NotFound()
        domain = [('employee_id', '=', employee.id)]

        searchbar_sortings = {
            'check_in_date': {'label': _('Check In'), 'order': 'check_in desc'},
            'check_out_date': {'label': _('Check Out'), 'order': 'check_out desc'},
            'worked_hours': {'label': _('Working Hours'), 'order': 'worked_hours desc'},
        }
        # Current month filter
        current_date = fields.Date.today()
        start_month = current_date.replace(day=1)
        end_month = current_date.replace(day=calendar.monthrange(current_date.year, current_date.month)[1])
        searchbar_filters = {
            'current_month': {'label': _('This Month'), 'domain': [('check_in', '>=', start_month), ('check_in', '<=', end_month)]},
            'all': {'label': _('All'), 'domain': []},
            'no_check_out': {'label': _('No Checkout'), 'domain': [('check_out', '=', False)]},
        }
        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search Working hours <span class="nolabel"> (in Attendance)</span>')},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'worked_hours': {'input': 'worked_hours', 'label': _('Working Hours')},
        }

        archive_groups = False
        if not sortby:
            sortby = 'check_in_date'
        if not filterby:
            filterby = 'current_month'
        sort_order = searchbar_sortings[sortby]['order']
        if groupby == 'worked_hours':
            sort_order = 'worked_hours, %s' % sort_order
        domain += searchbar_filters[filterby]['domain']
        attendance_count = attendance_obj.search_count(domain)
        # search only the document name
        if search and search_in:
            domain = AND([domain, [('worked_hours', 'ilike', search)]])
        pager = request.website.pager(
            url="/my/attendance",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=attendance_count,
            page=page,
            step=self._items_per_page
        )
        
        attendance = attendance_obj.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        if groupby == 'worked_hours':
            grouped_attendance = [attendance_obj.concat(*g)
                                  for k, g in groupbyelem(attendance, itemgetter('worked_hours'))]
        else:
            grouped_attendance = [attendance]
        
        values.update({
            'date': date_begin,
            'attendance': grouped_attendance,
            'page_name': 'My Attendance',
            'archive_groups': archive_groups,
            'default_url': '/my/attendance',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'search_in': search_in,
            'filterby': filterby,
            'sortby': sortby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'groupby': groupby,
        })
        return request.render("nl_attendance.portal_attendance_details", values)